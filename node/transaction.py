import time
import pickle
from ecdsa import SigningKey

from . import context
from . import server
from . import client

from .validator import validate_transaction


class TransactionManager:
    
    def __init__(self, signing_key, verifying_key):
        self.signing_key = signing_key
        self.verifying_key = verifying_key

        self.transaction_list = []
        self.transaction_set = set()
        self.digest_counter = 0
    
    def generate_transaction(self, data, to_pubkey):
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
        if tx[4] in self.transaction_set: return

        self.transaction_set.add(tx[4])
        self.transaction_list.append(tx)

        n_pendings = len(self.transaction_list) - self.digest_counter
        if context.AUTO_BLOCK_GEN:
            for i in range(self.digest_counter, len(self.transaction_list), context.TXS_PER_BLOCK):
                # block manager!
                print('plz make a block!')
                self.transaction_list[i:i+context.TXS_PER_BLOCK]
                pass
        else:
            print('## current # of pending tx: %d' % n_pendings)
                
        return
    
    def accept_transaction(self, tx):
        if not validate_transaction(tx):
            # invalid transaction
            return False

        if self.verifying_key == tx[0]:
            # ignore own transaction
            return False
        
        self.store_verified_transaction(tx)
        return True
    

