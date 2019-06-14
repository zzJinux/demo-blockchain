import hashlib
from ecdsa import SigningKey, VerifyingKey
from .context import DIFFICULTY_TARGET

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
    

# block == [ index, timestamp:int, prev_block_hash, transaction_list, block_producer, nonce ]

def serialize_block(block):
    index, timestamp, prev_block_hash, transaction_list, block_producer, nonce = block

    index_bytes = index.to_bytes(2, 'big')
    timestamp_bytes = timestamp.to_bytes(4, 'big')
    tx_len_bytes = len(transaction_list).to_bytes(2, 'big')

    barr = bytearray()
    barr += index_bytes
    barr += timestamp_bytes
    barr += prev_block_hash
    barr += tx_len_bytes

    for tx in transaction_list:
        barr += serialize_transaction(tx)

    barr += block_producer
    barr += nonce

    return bytes(barr)


def hash_block_bytes(block_bytes):
    return hashlib.sha256(block_bytes).digest()


def hash_block(block):
    return hash_block_bytes(serialize_block(block))


def validate_block(block):
    index = block[0]
    if index < 0:
        print('@@ INVALID_BLOCK: index < 0')
        return False
    elif index == 0 and block[2] != bytes(32):
        print('@@ INVALID_BLOCK: index == 0 but prev_hash non-zero')
        return False

    block_hash = hash_block(block)
    if block_hash >= DIFFICULTY_TARGET:
        print('@@ INVALID_BLOCK: fail on comparison on DIFFICULTY_TARGET')
        return False

    tx_list = block[3]
    for tx in tx_list:
        if not validate_transaction(tx):
            print('@@ INVALID_BLOCK: invalid transaction')
            return False

    return True
