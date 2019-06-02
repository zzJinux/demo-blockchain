from ecdsa import SigningKey, VerifyingKey

def validate_transaction(tx):
    message, signature, pubkey = tx
    vk = VerifyingKey.from_string(pubkey)
    return vk.verify(signature, message)
    