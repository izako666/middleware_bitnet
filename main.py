import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI

from data_classes.invoice import Invoice
from data_classes.transaction import Transaction

app = FastAPI()

import codecs
import json
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from dataclasses import asdict, dataclass, field
from typing import List, Optional
import os
import time
# Use a service account.
cred = credentials.Certificate("./firebase_privatekey.json")

firebase_app = firebase_admin.initialize_app(cred)

db = firestore.client()

# LND connection constants
REST_HOST = "https://mybitnet.com:8443"

# Firestore collection constants
BTC_ADDRESSES_COLLECTION = "bitcoin_addresses"
BACKEND_COLLECTION = "backend"
TRANSACTIONS_SUBCOLLECTION = "transactions"
INVOICES_SUBCOLLECTION = "invoices"
executor = ThreadPoolExecutor(max_workers=2)  # Allows running two tasks in separate threads

@app.on_event("startup")
async def on_startup():
    loop = asyncio.get_event_loop()

    # Run the streams in separate threads
    loop.run_in_executor(executor, subscribe_invoices_sync)
    loop.run_in_executor(executor, subscribe_transactions_sync)

    # Run the other tasks asynchronously in the main event loop
    #post_transactions(await get_transactions())
    # Uncomment if needed
    # post_invoices(await get_invoices())
def get_transactions(block_height_start=None) -> List[Transaction]:
    url = f"{REST_HOST}/v1/transactions"
    macaroon_path = 'lnd_admin.macaroon'
    # Confirm the macaroon file exists
    if not os.path.exists(macaroon_path):
        raise FileNotFoundError(f"Macaroon file not found at {macaroon_path}")

    # Read the macaroon file
    with open(macaroon_path, 'rb') as f:
        macaroon = codecs.encode(f.read(), 'hex').decode()


    headers = {"Grpc-Metadata-macaroon": macaroon}
    r = None
    if block_height_start:
       r = requests.get(url, headers=headers, data=json.dumps({'start_height': block_height_start, 'max_transactions': 0}))
    else:
       r = requests.get(url, headers=headers, verify=False)
    data = r.json()
    print("Retrieved transactions json")
    transactions_list: list = data['transactions']
    
    transactions: List[Transaction] = [Transaction.from_json(tx) for tx in transactions_list]
    return transactions

    
    
def post_transactions(transactions: List[Transaction]):
 for transaction in transactions:
  post_transaction(transaction=transaction)
        
def post_transaction(transaction: Transaction):
 print(f'searching for transaction owner of: {transaction.tx_hash}')
 for output_detail in transaction.output_details:
  if output_detail.is_our_address:
   print(f'checking address : {output_detail.address}')
   query = db.collection(BTC_ADDRESSES_COLLECTION).where('addresses', 'array_contains', output_detail.address)
   results = list(query.stream())
   if results:
    user_id = results[0].id
    doc = db.collection(BACKEND_COLLECTION).document(user_id).get()
    if not doc.exists:
     db.collection(BACKEND_COLLECTION).document(user_id).create({})
    tx_doc = db.collection(BACKEND_COLLECTION).document(user_id).collection(TRANSACTIONS_SUBCOLLECTION).document(transaction.tx_hash).get()
    if not tx_doc.exists:
     db.collection(BACKEND_COLLECTION).document(user_id).collection(TRANSACTIONS_SUBCOLLECTION).document(transaction.tx_hash).set(transaction.to_json())
    else:
     db.collection(BACKEND_COLLECTION).document(user_id).collection(TRANSACTIONS_SUBCOLLECTION).document(transaction.tx_hash).update(transaction.to_json())

def post_recent_transactions():
   macaroon_path = 'lnd_admin.macaroon'
 # Confirm the macaroon file exists
   if not os.path.exists(macaroon_path):
    raise FileNotFoundError(f"Macaroon file not found at {macaroon_path}")

    # Read the macaroon file
   with open(macaroon_path, 'rb') as f:
    macaroon = codecs.encode(f.read(), 'hex').decode()


   headers = {"Grpc-Metadata-macaroon": macaroon}

   r = requests.get(f'{REST_HOST}/v1/getinfo', headers=headers, verify=False)
   block_height: int = r.json()['block_height']
   new_block_height = block_height - 12
   post_transactions(get_transactions(block_height_start=new_block_height))
async def subscribe_transactions():
 url = f"{REST_HOST}/v1/transactions/subscribe"
 macaroon_path = 'lnd_admin.macaroon'
 # Confirm the macaroon file exists
 if not os.path.exists(macaroon_path):
  raise FileNotFoundError(f"Macaroon file not found at {macaroon_path}")

    # Read the macaroon file
 with open(macaroon_path, 'rb') as f:
  macaroon = codecs.encode(f.read(), 'hex').decode()


 headers = {"Grpc-Metadata-macaroon": macaroon}
 print('attempting to start transactions stream...')
 attempts = 0
 retries = 3
 while attempts < retries:
  try:
   with requests.get(url, headers=headers, stream=True, verify=False) as resp:
    print('transaction stream began')
    for raw_response in resp.iter_lines():
     print('transaction stream new data')
     json_response = json.loads(raw_response)
     transaction = Transaction.from_json(json_response)
     post_transaction(transaction=transaction)
  except requests.ConnectionError:
     print("transactions stream stopped, retrying...")
     attempts+= 1
     time.sleep(2 ** attempts)
     post_recent_transactions()

  except requests.Timeout:
     print('transactions stream stopped: timeout, retrying...')
     attempts+=1
     time.sleep(2 ** attempts)
     post_recent_transactions()
  except Exception as e:
     print(f'transaction stream stopped: unexcepted error {e}, retrying...')
     attempts+=1
     time.sleep(2**attempts)
     post_recent_transactions()








#INVOICES
def calculate_unix_timestamp(hours_ago: int) -> int:
    """
    Calculates the Unix timestamp for 'now - x_hours'.
    
    Args:
        hours_ago (int): The number of hours to subtract from the current time.

    Returns:
        int: Unix timestamp in seconds.
    """
    current_time = time.time()  # Current time in seconds since the Unix epoch
    timestamp = int(current_time - (hours_ago * 3600))  # Subtract 'x' hours (3600 seconds per hour)
    return timestamp



def get_invoices(creation_date_start=None) -> List[Invoice]:
    url = f"{REST_HOST}/v1/invoices"
    macaroon_path = 'lnd_admin.macaroon'
    
    # Confirm the macaroon file exists
    if not os.path.exists(macaroon_path):
        raise FileNotFoundError(f"Macaroon file not found at {macaroon_path}")

    # Read the macaroon file
    with open(macaroon_path, 'rb') as f:
        macaroon = codecs.encode(f.read(), 'hex').decode()

    headers = {"Grpc-Metadata-macaroon": macaroon}

    all_invoices: List[Invoice] = []
    index_offset = 0  # Start at offset 0
    num_max_invoices = 100  # Fetch 100 invoices per request (adjust as needed)
    more_invoices = True

    while more_invoices:
        params = {
            "index_offset": index_offset,
            "num_max_invoices": num_max_invoices
        }

        # Add the creation_date_start filter if provided
        if creation_date_start:
            params["creation_date_start"] = creation_date_start

        # Fetch invoices with pagination parameters
        response = requests.get(url, headers=headers, params=params, verify=False)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch invoices: {response.status_code} - {response.text}")

        data = response.json()

        # Parse invoices and add to the list
        invoices_list = data.get('invoices', [])
        if not invoices_list:
            break  # Exit if no more invoices are returned

        all_invoices.extend([Invoice.from_json(inv) for inv in invoices_list])

        # Update index_offset for pagination
        index_offset = data.get('last_index_offset', 0)
        more_invoices = len(invoices_list) >= num_max_invoices  # Stop if fewer results are returned

    print(f"Total invoices retrieved: {len(all_invoices)}")
    return all_invoices



def post_invoice(invoice: Invoice):
 print(f'searching for invoice owner of: {invoice.payment_addr} with fallback_addr: {invoice.fallback_addr}')
 if not invoice.fallback_addr:
   return
 query = db.collection(BTC_ADDRESSES_COLLECTION).where('addresses', 'array_contains', invoice.fallback_addr)
 results = list(query.stream())
 if results:
  user_id = results[0].id
  doc = db.collection(BACKEND_COLLECTION).document(user_id).get()
  if not doc.exists:
   db.collection(BACKEND_COLLECTION).document(user_id).create({})
  inv_doc = db.collection(BACKEND_COLLECTION).document(user_id).collection(INVOICES_SUBCOLLECTION).document(invoice.payment_addr).get()
  if not inv_doc.exists:
   db.collection(BACKEND_COLLECTION).document(user_id).collection(INVOICES_SUBCOLLECTION).document(invoice.payment_addr).set(invoice.to_json())
  else:
   db.collection(BACKEND_COLLECTION).document(user_id).collection(INVOICES_SUBCOLLECTION).document(invoice.payment_addr).update(invoice.to_json())


def post_invoices(invoices: List[Invoice]):
 for invoice in invoices:
  post_invoice(invoice=invoice)


def post_recent_invoices():
   creation_date_start = calculate_unix_timestamp(12)
   post_invoices(get_invoices(creation_date_start=creation_date_start))


async def subscribe_invoices():
 url = f"{REST_HOST}/v1/invoices/subscribe"
 macaroon_path = 'lnd_admin.macaroon'
 # Confirm the macaroon file exists
 if not os.path.exists(macaroon_path):
  raise FileNotFoundError(f"Macaroon file not found at {macaroon_path}")

    # Read the macaroon file
 with open(macaroon_path, 'rb') as f:
  macaroon = codecs.encode(f.read(), 'hex').decode()


 headers = {"Grpc-Metadata-macaroon": macaroon}
 print('attempting to start invoices stream...')
 attempts = 0
 retries = 3
 while attempts < retries:
  try:
   with requests.get(url, headers=headers, stream=True, verify=False) as resp:
    print('invoice stream began')
    for raw_response in resp.iter_lines():
     print('invoice stream new data')
     json_response = json.loads(raw_response)
     invoice = Invoice.from_json(json_response['result'])
     post_invoice(invoice=invoice)
  except requests.ConnectionError:
     print("invoice stream stopped, retrying...")
     attempts+= 1
     time.sleep(2 ** attempts)
     post_recent_invoices()
  except Exception as e:
     print(f'invoice stream stopped: unexcepted error {e}, retrying...')
     attempts+=1
     time.sleep(2**attempts)
     post_recent_invoices()



def subscribe_invoices_sync():
    asyncio.run(subscribe_invoices())  # Blocking call for the thread

def subscribe_transactions_sync():
    asyncio.run(subscribe_transactions())  # Blocking call for the thread
