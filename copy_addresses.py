import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore



cred = credentials.Certificate("./firebase_privatekey.json")

firebase_app = firebase_admin.initialize_app(cred)

db = firestore.client()

BTC_ADDRESSES_COLLECTION = "bitcoin_addresses"

account = "03449c36e9b4b0c17e27b6571884cabd3d913f28ed352a4f4c8fd5e1eb2a8ef5dc"

doc = db.collection(BTC_ADDRESSES_COLLECTION).document(account).get()
addresses = doc.get('addresses')
db.collection(BTC_ADDRESSES_COLLECTION).document(account).update({
    'change_addresses': addresses
})