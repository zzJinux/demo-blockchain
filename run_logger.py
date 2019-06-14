from http.server import BaseHTTPRequestHandler, HTTPServer
from sys import argv
from gui.guiLogger import WindowLogger
from threading import Thread

log = []

class LoggingServer(BaseHTTPRequestHandler):
    def _set_response(self):
        pass

    def do_GET(self):
        pass

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        log.append(post_data.decode('utf-8'))
        #print(log)

def run(server_class=HTTPServer, handler_class=LoggingServer, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    try:
        print('Start Logging Server...')
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == '__main__':
    http_server_thread = Thread(target=run)
    http_server_thread.start()
    wnd = WindowLogger(log)
    wnd.show()
