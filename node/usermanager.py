import threading

from . import server
from . import context

lock = threading.Lock()

class UserManager:

    def __init__(self):
        self.users = {}

    def register_handlers(self, server_instance):
        server_instance.add_handler(b'join', self._join_handler)
        server_instance.add_handler(b'bye-', self._bye_handler)
        return

    def _join_handler(self, peer_data):
        host, port, pubkey, name = peer_data
        addr = (host, port)

        self.add_user(pubkey, name, addr)
        return b'ok--', (context.PUBLIC_KEY.to_string(), context.NAME)
    
    def _bye_handler(self, pubkey):
        self.remove_user(pubkey)
        return

    def get_user(self, pubkey):
        return self.users.get(pubkey[:4])

    def add_user(self, pubkey, name, server_addr):
        if pubkey in self.users:
            return None

        lock.acquire()
        self.users[pubkey[:4]] = (pubkey, name, server_addr)
        lock.release()

        print('+++ Number of Participation %d' % len(self.users))

        return pubkey

    def remove_user(self, pubkey):
        if pubkey[:4] not in self.users:
            return

        lock.acquire()
        del self.users[pubkey[:4]]
        lock.release()

        print('--- Number of Participation %d' % len(self.users))

        return

    def get_user_list(self):
        lock.acquire()
        user_list = list(iter(self.users.values()))
        lock.release()

        return map(lambda x: x[2], user_list)
