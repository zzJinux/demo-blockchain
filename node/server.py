import socketserver
import traceback
import pickle


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        assert type(self.server) == ThreadedTCPServer

        print('@@ [%s:%d] is connected' % self.client_address)

        try:
            msg = self.request.recv(1024)
            cmd, data = msg[:4], (pickle.loads(msg[4:]) if len(msg) > 4 else None)

            handler_func = self.server.get_handler(cmd)
            reply = handler_func(data)
            if reply:
                if len(reply) > 1:
                    # cmd & data
                    cmd, data = reply[0], reply[1]
                    self.request.send(cmd + pickle.dumps(data))
                else:
                    # cmd only
                    self.request.send(reply[0])
            else:
                # no data to respond
                pass
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
        

        print('@@ [%s:%d], connection terminates' % self.client_address)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handler_mapping = dict()

    def add_handler(self, cmd, handler_func):
        assert type(cmd) == bytes
        assert len(cmd) == 4
        assert callable(handler_func)

        self.handler_mapping[cmd] = handler_func
    
    def get_handler(self, cmd):
        assert type(cmd) == bytes
        assert len(cmd) == 4

        return self.handler_mapping[cmd]
