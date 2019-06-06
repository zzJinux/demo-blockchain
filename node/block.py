from .context import TXS_PER_BLOCK

class BlockManager:

    def __init__(self, tx_manager):
        self.tx_manager = tx_manager
        tx_manager.add_listener(self.handle_tx_mutation)
        self.block_dict = dict()
        self.next_block_index = 0
    
    def handle_tx_mutation(self):
        tx_queue = self.tx_manager.transaction_queue
        queue_size = len(tx_queue)
        print(f'@@ current # of pending tx for block gen: {queue_size}')
        if queue_size < TXS_PER_BLOCK:
            return

        print('** You are ready to generate blocks')
        return

    def generate_block(self):
        tx_queue = self.tx_manager.transaction_queue
        queue_size = len(tx_queue)
        if queue_size < TXS_PER_BLOCK:
            print('** block generation not ready')
            print(f'@@ current # of pending tx for block gen: {queue_size}')
            return
        
        counter = TXS_PER_BLOCK
        while counter > 0:
            # TODO
            tx = tx_queue.popleft()
            counter -= 1

        # TODO

        self.handle_tx_mutation()
        return

