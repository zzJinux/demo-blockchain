from threading import Thread
import socket
import pickle

from ecdsa import SigningKey

from . import server
from .transaction import TransactionManager
from .usermanager import UserManager

# server loop helper
def run_server(server_instance):
    try:
        server_instance.serve_forever()
    except KeyboardInterrupt:
        server_instance.shutdown()
    finally:
        server_instance.server_close()


class NodeClient:

    def __init__(
        self, name = 'unnamed', host = 'localhost', port = 0, is_miner = False
    ):
        self.name = name

        self.server_host = host
        self.server_port = port
        self.server_instance = None

        # generate key pair
        sk = SigningKey.generate()
        self.signing_key =  sk.to_string()
        self.verifying_key = sk.get_verifying_key().to_string()

        # shorthand_id represents lower 8-byte of verifying key
        self.shorthand_id = ''.join(f'{x:02x}' for x in self.verifying_key[:4])

        self.tx_manager = TransactionManager(self.signing_key, self.verifying_key)
        self.user_manager = UserManager()

        self.is_miner = is_miner

    def start(self):
        print(f'@@ starts to initiate node {self.name}...')

        server_instance = server.ThreadedTCPServer(
            (self.server_host, self.server_port),
            server.ThreadedTCPRequestHandler
        )
        self.server_host, self.server_port = server_instance.server_address
        print(f'@@ server binds to [{self.server_host}:{self.server_port}]')

        server_instance.add_handler(b'join', self.handle_join)
        server_instance.add_handler(b'bye-', self.handle_bye)
        server_instance.add_handler(b'tx--', self.handle_tx_receive)
        self.server_instance = server_instance

        # starts non-blocking server
        server_thread = Thread(target=run_server, args=(server_instance,))
        server_thread.daemon = True
        server_thread.start()
        print(f'@@ server starts at thread [{server_thread.name}]')

        print(f'** Hi, {self.name}. Your shorthand id is {self.shorthand_id} **')
        print(f'** Your server address is {self.server_host}:{self.server_port} **')

        return
        
    def join(self, peer_address):
        with socket.socket() as sock:
            sock.connect(peer_address)

            # inform my own server address, public key, name
            sock.send(
                b'join' + pickle.dumps((
                    self.server_host,
                    self.server_port,
                    self.verifying_key,
                    self.name
                ))
            )
            msg = sock.recv(1024)

        cmd, data = msg[:4], pickle.loads(msg[4:])
        if cmd != b'ok--':
            print(f'@@ expects cmd to be "ok--" but was "{cmd}')
            raise Exception
        
        peer_pubkey, peer_name = data
        self.user_manager.add_user(peer_pubkey, peer_name, peer_address)
        return

    def handle_join(self, peer_data):
        host, port, pubkey, name = peer_data
        addr = (host, port)

        self.user_manager.add_user(pubkey, name, addr)
        return b'ok--', (self.verifying_key, self.name)

    def quit(self):
        peer_addresses = self.user_manager.get_user_list()
        threads = []

        print('** Say goodbye to all peers! **')
        print('@@ send "bye" messages to all peers')
        for addr in peer_addresses:
            thread = Thread(target=self.bye, args=(addr,))
            threads.append(thread)
            thread.start()

        # join all threads before server shutdown
        for thr in threads:
            thr.join()

        print('@@ now shutdown...')
        self.server_instance.shutdown()
        return

    def bye(self, peer_address):
        print('** Say goodbye to [%s:%s] **' % peer_address)
        with socket.socket() as sock:
            sock.connect(peer_address)
            # one-way byebye
            sock.send(b'bye-' + pickle.dumps(self.verifying_key))

        # return without waiting
        return
    
    def handle_bye(self, verifying_key):
        self.user_manager.remove_user(verifying_key)
        return

    def generate_transaction(self, dest_id, data):
        print(f'dest_id: {dest_id}')
        user = self.user_manager.get_user(bytes.fromhex(dest_id))
        tx = self.tx_manager.generate_transaction(user[0], data)
        self.broadcast_transaction(tx)

        return
    
    def broadcast_transaction(self, tx):
        print('@@ broadcast transaction to all known peers')
        peer_addresses = self.user_manager.get_user_list()
        threads = []

        # multithreaded broadcasting
        for addr in peer_addresses:
            thread = Thread(target=self.send_transaction_single, args=(tx, addr))
            threads.append(thread)
            thread.start()

        # join before return
        for thr in threads:
            thr.join()
        
        return
    
    def send_transaction_single(self, tx, peer_addr):
        print('@@ sending one transaction to peer [%s:%s]' % peer_addr)

        with socket.socket() as sock:
            sock.connect(peer_addr)

            sock.send(b'tx--' + pickle.dumps(tx))
            reply = sock.recv(1024)

            cmd = reply[:4]
            if cmd != b'ok--':
                print(f'@Error expects cmd to be "ok--" but was "{cmd}')
                raise Exception

        return
    
    def handle_tx_receive(self, tx):
        accepted = self.tx_manager.accept_transaction(tx)
        if accepted: self.broadcast_transaction(tx)
        
        return (b'ok--',)
    
    def generate_block(self, _, __):
        print('generate block!! TODOTODO')
        pass
    

