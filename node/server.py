import socketserver
import pickle

from . import context

# registered from outside the module
handler_mapping = dict()

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        print('@@ [%s:%d] is connected' % self.client_address)

        try:
            msg = self.request.recv(1024)
            cmd, data = msg[:4], (pickle.loads(msg[4:]) if len(msg) > 4 else None)

            reply = handler_mapping[cmd](data)
            if reply:
                cmd, data = reply[0], (reply[1] if len(reply) > 1 else None)
                self.request.send(cmd + pickle.dumps(data))
            else:
                pass
        except Exception as e:
            print(e)
        

        print('@@ [%s:%d], connection terminates' % self.client_address)


class ThreadedTCPserver(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass
