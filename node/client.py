from threading import Thread
import socket
import pickle

from . import context

def quit(server_instance):
    print('## quitting')
    peer_addresses = context.USER_POOL.get_peer_addresses()
    threads = []

    # say goodbye to pees in multithreaded way
    print('## say goodbye to peers!')
    for addr in peer_addresses:
        thread = Thread(target=bye, args=(addr,))
        threads.append(thread)
        thread.start()

    # join before shutdown server
    for thr in threads:
        thr.join()

    print('## now shutdown...')
    server_instance.shutdown()
    return


def bye(peer_address):
    print('## say goodbye to peer [%s:%s]' % peer_address)
    with socket.socket() as sock:
        sock.connect(peer_address)
        # one-way byebye
        sock.send(b'bye-' + pickle.dumps(context.PUBLIC_KEY.to_string()))

    # return without waiting
    return


def join(peer_address):
    print('## joining to peer [%s:%s]' % peer_address)
    with socket.socket() as sock:
        sock.connect(peer_address)

        # inform my own server address, public key, name
        sock.send(
            b'join' + pickle.dumps((
                context.HOST,
                context.PORT,
                context.PUBLIC_KEY.to_string(),
                context.NAME
            ))
        )
        msg = sock.recv(1024)

    cmd, data = msg[:4], pickle.loads(msg[4:])
    if cmd != b'ok--': raise Exception
    
    peer_pubkey, peer_name = data
    context.USER_POOL.addUser(peer_pubkey, peer_name, peer_address)
    print('## successfully joined to %s' % peer_name)
    return


def broadcast(message):
    print('## broadcast message to all known peers!')
    peer_addresses = context.USER_POOL.get_peer_addresses()
    threads = []

    # multithreaded broadcasting
    for addr in peer_addresses:
        thread = Thread(target=send_message, args=(addr, message))
        threads.append(thread)
        thread.start()

    # join before return
    for thr in threads:
        thr.join()
    
    return


def send_message(addr, message):
    print('## sending message to peer [%s:%s]' % addr)
    with socket.socket() as sock:
        sock.connect(addr)

        sock.send(message)
        reply = sock.recv(1024)

        cmd = reply[:4]
        if cmd != b'ok--': raise Exception

    return
