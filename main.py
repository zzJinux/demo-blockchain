import sys
import threading
import socketserver

import node.context as context
import node.server as server
import node.client as client
from node.transaction import TransactionManager
from node.usermanager import UserManager


def runServer(server_instance):
    try:
        server_instance.serve_forever()
    except KeyboardInterrupt:
        server_instance.shutdown()
    finally:
        server_instance.server_close()


def runNode():
    print('...initiating node')
    server_instance = server.ThreadedTCPserver(
        (context.HOST, context.PORT),
        server.ThreadedTCPRequestHandler
    )
    print('...bind to [%s:%s]' % server_instance.server_address)
    context.HOST, context.PORT = server_instance.server_address

    print(f'Hi {context.NAME}.')

    shorthand_id = ''.join(f'{x:02x}' for x in context.PUBLIC_KEY.to_string()[:4])
    print(f'Your identity (shortened): {shorthand_id}')

    # non-blocking server
    server_thread = threading.Thread(target=runServer, args=(server_instance,))
    server_thread.daemon = True
    server_thread.start()

    tx_manager = TransactionManager()
    tx_manager.register_handlers()
    context.USER_POOL.register_handlers()

    # handle command-line input
    # blocking client
    while True:
        try:
            command_text = input('> ').strip()
        except:
            client.quit(server_instance)
            return

        if command_text.startswith('quit'):
            client.quit(server_instance)
            return
        elif command_text.startswith('join '):
            # skip validating :peer_address:
            host, port = command_text[len('join '):].split(':', 1)
            port = int(port)

            client.join((host, port))
        elif command_text.startswith('tx '):
            dest_id, data = command_text.split(' ')[1:]
            assert len(dest_id) == 8

            user = context.USER_POOL.get_user(bytes.fromhex(dest_id))

            tx_manager.generate_transaction(data.encode(), user[0])
        elif command_text.startswith('blk '):
            if not context.IS_MINER: continue
            
            print('## not ready to generate block --- TODO')
        elif command_text.startswith('inspect peers'):
            pass
        elif command_text.startswith('inspect txpool'):
            pass
        else:
            pass


if __name__ == "__main__":
    argc = len(sys.argv)
    context.NAME = sys.argv[1]
    if(argc > 2): context.PORT = int(sys.argv[2])
    if(argc > 3): context.IS_MINER = sys.argv[3] == 'miner'

    runNode()
