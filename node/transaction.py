import time
import pickle

from . import context
from . import server
from . import client

from .validator import validate_transaction


class TransactionManager:
    
    def __init__(self):
        self.transaction_list = []
        self.transaction_set = set()
        self.digest_counter = 0
    
    def register_handlers(self):
        server.handler_mapping[b'tx--'] = self._new_transaction_handler
    
    def _new_transaction_handler(self, tx):
        if not validate_transaction(tx): return

        if context.PUBLIC_KEY.to_string() == tx[0]:
            # ignore own transaction
            return (b'ok--',)
        
        self.store_verified_transaction(tx)
        self.broadcast_transaction(tx)

        return (b'ok--',)

    def generate_transaction(self, data, to_pubkey):
        assert isinstance(data, bytes)
        assert isinstance(to_pubkey, bytes)

        from_pubkey = context.PUBLIC_KEY.to_string()
        timestamp = int(time.time()) # in seconds

        tx_bytes = from_pubkey + to_pubkey + data + bytes([timestamp])
        signature = context.PRIVATE_KEY.sign(tx_bytes)
        tx = (from_pubkey, to_pubkey, data, timestamp, signature)

        self.store_verified_transaction(tx)
        self.broadcast_transaction(tx)
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
    
    def broadcast_transaction(self, tx):
        client.broadcast(b'tx--' + pickle.dumps(tx))
