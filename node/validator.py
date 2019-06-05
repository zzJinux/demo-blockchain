from ecdsa import SigningKey, VerifyingKey

def validate_transaction(tx):
    pubkey = tx[0]
    signature = tx[4]
    vk = VerifyingKey.from_string(pubkey)
    return vk.verify(signature, b''.join(tx[:4]))
    