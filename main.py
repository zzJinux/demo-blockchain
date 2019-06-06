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
            dest_id, str = command_text.split(' ')[1:]
            assert len(dest_id) == 8

            node_client.generate_transaction(dest_id, str.encode())
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
    name = sys.argv[1]
    host = 'localhost'
    port = int(sys.argv[2]) if argc > 2 else 0
    is_miner = sys.argv[3] == 'miner' if argc > 3 else False

    node_client = NodeClient(name, host, port, is_miner)
    node_client.start()

    cli_loop(node_client)
