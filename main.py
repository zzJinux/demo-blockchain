import sys

from node.client import NodeClient


def cli_loop(node_client):
    while True:
        try:
            command_text = input('> ').strip()
        except:
            node_client.quit()
            return

        if command_text.startswith('quit'):
            node_client.quit()
            return
        elif command_text.startswith('join '):
            # skip validating :peer_address:
            host, port = command_text[len('join '):].split(':', 1)
            port = int(port)

            node_client.join((host, port))
        elif command_text.startswith('tx '):
            dest_id, text = command_text.split(' ')[1:]
            assert len(dest_id) == 8

            node_client.generate_transaction(dest_id, text.encode())
        elif command_text.startswith('blk '):
            if not node_client.is_miner: continue
            
            node_client.generate_block()
        elif command_text.startswith('inspect peers'):
            pass
        elif command_text.startswith('inspect txpool'):
            pass
        else:
            pass


if __name__ == "__main__":
    argc = len(sys.argv)
    is_miner = sys.argv[1] == 'miner' if argc > 1 else False
    if argc < 2:
        print('# Usage')
        print('$ main.py <"miner" | ELSE> [ <name> [ <host>:<port> ]]')
    name = sys.argv[2] if argc > 2 else 'unnamed'
    host = sys.argv[3] if argc > 3 else 'localhost'
    port = int(sys.argv[4]) if argc > 4 else 0

    node_client = NodeClient(name, host, port, is_miner)
    node_client.start()

    cli_loop(node_client)


class GuiHelper:
    
    def __init__(self, node_client):
        self.node_client = node_client
    
    def quit(self):
        self.node_client.quit()
        return
    
    def join(self, str1):
        try:
            host, port = str1.split(':', 1)
            port = int(port)
        except:
            print('Invalid peer address.')
            return

        self.node_client.join((host, port))
        return
    
    def tx(self, str1, str2):
        assert len(str1) == 8

        self.node_client.generate_transaction(str1, str2.encode())
        return
    
    def blk(self, str1, str2):
        if not node_client.is_miner: return
        pass

