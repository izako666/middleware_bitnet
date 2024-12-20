import base64, codecs, json, requests

REST_HOST = 'mybitnet.com:8443'
MACAROON_PATH = 'lnd_admin.macaroon'


from typing import List, Dict, Any


class Input:
    def __init__(self, txid_str: str, txid_bytes: str, output_index: int):
        """
        Represents a single transaction input.

        :param txid_str: Transaction ID as a string.
        :param txid_bytes: Transaction ID as bytes (hex-encoded).
        :param output_index: Index of the output being spent.
        """
        self.txid_str = txid_str
        self.txid_bytes = txid_bytes
        self.output_index = output_index

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> "Input":
        """
        Creates an Input instance from a JSON-like dictionary.

        :param json: Dictionary containing txid_str, txid_bytes, and output_index.
        :return: Input instance.
        """
        return cls(
            txid_str=json["txid_str"],
            txid_bytes=json["txid_bytes"],
            output_index=json["output_index"],
        )

    def to_json(self) -> Dict[str, Any]:
        """
        Converts the Input instance to a JSON-serializable dictionary.

        :return: Dictionary representation of the Input instance.
        """
        return {
            "txid_str": self.txid_str,
            "txid_bytes": self.txid_bytes,
            "output_index": self.output_index,
        }


class Outputs:
    def __init__(self, outputs: Dict[str, int]):
        """
        Represents the transaction outputs as a map of address to amount.

        :param outputs: Dictionary where the key is the address (str), and value is the amount (int).
        """
        self.outputs = outputs

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> "Outputs":
        """
        Creates an Outputs instance from a JSON-like dictionary.

        :param json: Dictionary containing addresses as keys and amounts as values.
        :return: Outputs instance.
        """
        outputs = {key: int(value) for key, value in json.items()}
        return cls(outputs=outputs)

    def to_json(self) -> Dict[str, int]:
        """
        Converts the Outputs instance to a JSON-serializable dictionary.

        :return: Dictionary representation of Outputs.
        """
        return self.outputs


class RawTransactionData:
    def __init__(self, inputs: List[Input], outputs: Outputs):
        """
        Represents raw transaction data consisting of inputs and outputs.

        :param inputs: List of Input instances.
        :param outputs: Outputs instance.
        """
        self.inputs = inputs
        self.outputs = outputs

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> "RawTransactionData":
        """
        Creates a RawTransactionData instance from a JSON-like dictionary.

        :param json: Dictionary containing inputs and outputs.
        :return: RawTransactionData instance.
        """
        inputs = [Input.from_json(i) for i in json["inputs"]]
        outputs = Outputs.from_json(json["outputs"])
        return cls(inputs=inputs, outputs=outputs)

    def to_json(self) -> Dict[str, Any]:
        """
        Converts the RawTransactionData instance to a JSON-serializable dictionary.

        :return: Dictionary representation of RawTransactionData.
        """
        return {
            "inputs": [i.to_json() for i in self.inputs],
            "outputs": self.outputs.to_json(),
        }







# url = f'https://{REST_HOST}/v2/wallet/utxos'
# macaroon = codecs.encode(open(MACAROON_PATH, 'rb').read(), 'hex')
# headers = {'Grpc-Metadata-macaroon': macaroon}
# data = {
#   'min_confs': 4,
#   'max_confs': 99999,
#   'account': "03449c36e9b4b0c17e27b6571884cabd3d913f28ed352a4f4c8fd5e1eb2a8ef5dc",
#   'unconfirmed_only': False,
# }
# r = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
# print(r.json())
# utxos = r.json()['utxos']
# # {
# #    "utxos": <Utxo>,
# amount_in_sat = 400
# bitcoin_receiver_address = "bc1qrv7yry2ys2k8hpm80clf8g328gtjzd0df2gm4a"


# url = f'https://{REST_HOST}/v2/wallet/utxos/leases'
# macaroon = codecs.encode(open(MACAROON_PATH, 'rb').read(), 'hex')
# headers = {'Grpc-Metadata-macaroon': macaroon}
# data = {
# }
# r = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
# print(r.json())
# leases: list = r.json()['locked_utxos']
# print(f'leases count: {len(leases)}')
# locked_utxos = []
# for utxo in utxos:
#     for lease in leases:
#         if utxo['pk_script'] == lease['pk_script']:
#             locked_utxos.append(lease)
# print(locked_utxos)
# for locked_utxo in locked_utxos:   
#  url = f'https://{REST_HOST}/v2/wallet/utxos/release'      
#  data = {
#     'id': locked_utxo['id'],
#     'outpoint': locked_utxo['outpoint']
#  }      

#  r = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
#  print(r.json())




REST_HOST = 'mybitnet.com:8443' #1443 #192.168.178.146
MACAROON_PATH = 'lnd_admin.macaroon'
TLS_PATH = './pythonfunctions/fullchain.pem'

url = f'https://{REST_HOST}/v2/wallet/utxos'
macaroon = codecs.encode(open(MACAROON_PATH, 'rb').read(), 'hex')
headers = {'Grpc-Metadata-macaroon': macaroon}
data = {
  'min_confs': 0,
  'max_confs': 10,
  'account': "default",
  'unconfirmed_only': False, #True #False
}
r = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
print(r.json())