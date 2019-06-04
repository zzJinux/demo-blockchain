from ecdsa import SigningKey
from . import usermanager

HOST = 'localhost'
PORT = 0
PRIVATE_KEY = SigningKey.generate()
PUBLIC_KEY  = PRIVATE_KEY.get_verifying_key()
NAME = 'unnamed'
IS_MINER = False
USER_POOL = usermanager.UserManager()

AUTO_BLOCK_GEN = False
TXS_PER_BLOCK = 10
