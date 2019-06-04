import threading

from . import server
from . import context

lock = threading.Lock()

class UserManager:

    def __init__(self):
        self.users = {}

    def register_handlers(self):
        server.handler_mapping[b'join'] = self._join_handler
        server.handler_mapping[b'bye-'] = self._bye_handler
        return

    def _join_handler(self, peer_data):
        host, port, pubkey, name = peer_data
        addr = (host, port)

        self.addUser(pubkey, name, addr)
        return b'ok--', (context.PUBLIC_KEY.to_string(), context.NAME)
    
    def _bye_handler(self, pubkey):
        self.removeUser(pubkey)
        return

    def addUser(self, pubkey, name, server_addr):
        if pubkey in self.users:
            return None

        lock.acquire()
        self.users[pubkey] = (name, server_addr)
        lock.release()

        print('[%s] join' % name)
        print('+++ Number of Participation %d' % len(self.users))

        return pubkey

    def removeUser(self, pubkey):
        if pubkey not in self.users:
            return

        lock.acquire()
        name = self.users[pubkey][0]
        del self.users[pubkey]
        lock.release()

        print('[%s] quit' % name)
        print('--- Number of Participation %d' % len(self.users))

        return

    def get_peer_addresses(self):
        lock.acquire()
        peer_list = list(iter(self.users.values()))
        lock.release()

        return map(lambda x: x[1], peer_list)
