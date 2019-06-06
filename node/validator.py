import hashlib
from ecdsa import SigningKey, VerifyingKey

# tx_raw == [ from_pubkey, to_pubkey, data, timestamp:int ]
# tx == ( from_pubkey, to_pubkey, data, timestamp:int, signature )

def serialize_transaction(tx):
    from_pubkey, to_pubkey, data, timestamp = tx[:4]
    
    data_len_bytes = len(data).to_bytes(2, 'big')
    timestamp_bytes = timestamp.to_bytes(4, 'big')

    return from_pubkey + to_pubkey + data_len_bytes + data + timestamp_bytes


def sign_transaction(tx_raw, singing_key):
    sk = SigningKey.from_string(singing_key)
    tx_bytes = serialize_transaction(tx_raw)
    return sk.sign(tx_bytes)


def validate_transaction(tx):
    verifying_key = tx[0]
    vk = VerifyingKey.from_string(verifying_key)
    signature = tx[4]
    tx_bytes = serialize_transaction(tx)
    return vk.verify(signature, tx_bytes)
    
