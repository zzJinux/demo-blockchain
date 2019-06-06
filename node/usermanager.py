import threading

from . import server
from . import context

lock = threading.Lock()

class UserManager:

    def __init__(self):
        self.users = {}

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
