import time
import pickle
import threading
from collections import deque
from ecdsa import SigningKey

from . import context
from . import server
from . import client

from .validator import sign_transaction, validate_transaction
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

        self.transaction_queue = deque()
        self.rlock = threading.RLock()
        self.transaction_dict = dict()
        self.transaction_pending_dict = dict()

        # _WARNING_ never reassign
        self.transaction_list_str = []

        self.listener_list = []
    
    def generate_transaction(self, to_pubkey, data):
        assert isinstance(data, bytes)
        assert isinstance(to_pubkey, bytes)

        # tx_raw == [ from_pubkey, to_pubkey, data, timestamp:int ]
        tx_raw = [ self.verifying_key, to_pubkey, data, int(time.time()) ]
        signature = sign_transaction(tx_raw, self.signing_key)

        tx = (*tx_raw, signature)

        self.store_verified_transaction(tx)
        return tx
    
    def store_verified_transaction(self, tx):
        # check if already stored
        with self.rlock:
            if tx[4] in self.transaction_dict: return False

            self.transaction_dict[tx[4]] = tx
            self.transaction_list_str.append(transaction_to_text(tx))

            self.transaction_pending_dict[tx[4]] = tx
            self.transaction_queue.append(tx)

            for listener in self.listener_list:
                listener()

        return True
    
    def store_sliently(self, tx):
        if tx[4] in self.transaction_dict: return

        with self.rlock:
            self.transaction_dict[tx[4]] = tx
            self.transaction_list_str.append(transaction_to_text(tx))

            if tx[4] in self.transaction_pending_dict:
                del self.transaction_pending_dict[tx[4]]
            
            self.transaction_queue[:] = list(
                filter(lambda qtx: qtx[4] in self.transaction_pending_dict, self.transaction_queue)
            )
        
    def accept_transaction(self, tx):
        if not validate_transaction(tx):
            # invalid transaction
            return False

        if self.verifying_key == tx[0]:
            # ignore own transaction
            return False
        
        return self.store_verified_transaction(tx)
    
    def add_listener(self, listener):
        assert callable(listener)
        self.listener_list.append(listener)

