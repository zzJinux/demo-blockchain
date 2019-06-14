import threading
import time

from .context import TXS_PER_BLOCK, DIFFICULTY_TARGET
from .validator import serialize_block, hash_block, hash_block_bytes, validate_block
from .toolbox import bytes_to_hexstring, mylog

def block_to_text(block):
    str_list = [
        'index: %s' % block[0],
        'prev: %s' % bytes_to_hexstring(block[2][:4]),
        'nonce: %d' % int.from_bytes(block[5], 'big')
    ]

    return ', '.join(str_list)

def find_nonce(block):
    assert block[5] == b''

    barr = bytearray(serialize_block(block))
    barr.extend(bytearray(4))
    
    block_hash = None
    nonce = 0
    while True:
        barr[-4:] = nonce.to_bytes(4, 'big')
        block_hash = hash_block_bytes(barr)
        if block_hash < DIFFICULTY_TARGET:
            break
        nonce += 1
    
    block[5] = nonce.to_bytes(4, 'big')


def new_raw_block(index, timestamp, prev_hash, tx_list, prod_key):
    return [index, timestamp, prev_hash, tx_list, prod_key, b'']


class BlockManager:

    def __init__(self, tx_manager, signing_key):
        self.tx_manager = tx_manager
        self.signing_key = signing_key
        self.block_list = []
        self.block_pool = set()
        self.next_index = 0

        # _WARNING_ never reassign
        self.block_list_str = []

        self.rlock = threading.RLock()

        tx_manager.add_listener(self.handle_tx_queue_mutation)
    
    def handle_tx_queue_mutation(self, processed_list):
        tx_queue = self.tx_manager.transaction_queue
        queue_size = len(tx_queue)
        mylog(f'BLOCK: # pending tx: {queue_size}, not enough')
        mylog(f'BLOCK: current # of pending tx for block gen: {queue_size}')

        self.tx_manager.consume_transactions(processed_list)
        
        if queue_size < TXS_PER_BLOCK:
            return
        else:
            mylog('BLOCK: READY to generate block')
            return


    def generate_block(self):
        tx_queue = self.tx_manager.transaction_queue

        with self.rlock:
            queue_size = len(tx_queue)
            if queue_size < TXS_PER_BLOCK:
                mylog(f'BLOCK: # pending tx: {queue_size}, not enough')
                return None
            
            prev_hash = hash_block(self.block_list[self.next_index - 1]) if self.next_index > 0 else bytes(32)
            tx_list = []
            i = TXS_PER_BLOCK
            while i > 0:
                tx = tx_queue.popleft()
                tx_list.append(tx)
                i -= 1

            self.handle_tx_queue_mutation(tx_list)
            
            block_raw = new_raw_block(
                self.next_index, int(time.time()),
                prev_hash, tx_list, self.signing_key
            )

            mylog('BLOCK: nonce calcuation START')
            find_nonce(block_raw)
            mylog('BLOCK: nonce calcuation END')
            self.next_index += 1
            self.store_verified_block(block_raw)

        return block_raw

    def store_verified_block(self, block):
        with self.rlock:
            old_list = self.block_list[block[0]:]
            for bl in old_list:
                self.block_pool.remove(hash_block(bl))

            self.block_list[block[0]:] = [block]
            self.next_index = len(self.block_list)
            self.block_list_str[:] = [
                block_to_text(blk) for blk in self.block_list
            ]
            self.block_pool.add(hash_block(block))
            for tx in block[3]:
                self.tx_manager.store_sliently(tx)

    def accept_block(self, block):
        if self.signing_key == block[4]:
            # ignore a block generated by self
            mylog('# BLOCK: DISCARD generated by self')
            return False
        
        if not validate_block(block):
            # discard invalid block
            mylog('# BLOCK: DISCARD: invalid block')
            return False

        index = block[0]
        if index > self.next_index:
            # assume this case won't happen
            mylog('# BLOCK: DISCARD index assumption violation')
            return False

        if ((index == 0 and block[2] != bytes(32))
            or (index > 0 and block[2] != hash_block(self.block_list[index - 1]))
        ):

            # prev block not equals
            mylog('# BLOCK: DISCARD previous block mismatch')
            return False

        if index == self.next_index - 1:
            if block[1] < self.block_list[index][1]:
                # take earlier block
                mylog('# BLOCK: RACE')
                self.next_index -= 1
            else:
                mylog('# BLOCK: DISCARD old block')
                return False
        
        self.store_verified_block(block)
        mylog(f'# BLOCK: ACCEPTED length: {self.next_index}')

        return True
