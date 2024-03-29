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
            if len(dest_id) < 8:
                dest_id = dest_id.ljust(10, '0')

            node_client.generate_transaction(dest_id, text.encode())
        elif command_text.startswith('blk'):
            if not node_client.is_miner: continue
            
            node_client.generate_block(None, None)
        elif command_text.startswith('inspect peers'):
            pass
        elif command_text.startswith('inspect tx'):
            print('\n'.join(node_client.get_transaction_list_str()))
        elif command_text.startswith('inspect q'):
            print('\n'.join(node_client.get_transaction_pending_list_str()))
        elif command_text.startswith('inspect blk'):
            print('\n'.join(node_client.get_block_list_str()))
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
