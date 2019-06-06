import time
import pickle
from ecdsa import SigningKey

from . import context
from . import server
from . import client

from .validator import validate_transaction
from .toolbox import bytes_to_hexstring

def transaction_to_text(tx):
    str_list = [
        'msg: %s' % tx[2].decode(),
        'from: %s' % bytes_to_hexstring(tx[0][:4]),
        'to: %s' % bytes_to_hexstring(tx[1][:4])
    ]

    return ', '.join(str_list)


class TransactionManager:
    
    def __init__(self, signing_key, verifying_key):
        self.signing_key = signing_key
        self.verifying_key = verifying_key

        self.transaction_list = []
        self.transaction_dict = dict()
        self.digest_counter = 0

        # _WARNING_ never reassign
        self.transaction_list_str = []
    
    def generate_transaction(self, to_pubkey, data):
        assert isinstance(data, bytes)
        assert isinstance(to_pubkey, bytes)

        from_pubkey = self.verifying_key
        timestamp_bytes = int(time.time()).to_bytes(4, 'big') # in seconds

        tx_bytes = from_pubkey + to_pubkey + data + timestamp_bytes
        signature = SigningKey.from_string(self.signing_key).sign(tx_bytes)
        tx = (from_pubkey, to_pubkey, data, timestamp_bytes, signature)

        self.store_verified_transaction(tx)
        return tx
    
    def store_verified_transaction(self, tx):
        # check if already stored
        if tx[4] in self.transaction_dict: return False

        self.transaction_dict[tx[4]] = tx
        self.transaction_list.append(tx)
        self.transaction_list_str.append(transaction_to_text(tx))

        n_pendings = len(self.transaction_list) - self.digest_counter
        if context.AUTO_BLOCK_GEN:
            for i in range(self.digest_counter, len(self.transaction_list), context.TXS_PER_BLOCK):
                # block manager!
                print('plz make a block!')
                self.transaction_list[i:i+context.TXS_PER_BLOCK]
                pass
        else:
            print('## current # of pending tx for block gen: %d' % n_pendings)
                
        return True
    
    def accept_transaction(self, tx):
        if not validate_transaction(tx):
            # invalid transaction
            return False

        if self.verifying_key == tx[0]:
            # ignore own transaction
            return False
        
        return self.store_verified_transaction(tx)
    

