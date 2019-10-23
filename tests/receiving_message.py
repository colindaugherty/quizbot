from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class ExampleJSONHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        len = int(self.headers.get('Content-Length'))
        data = json.loads(self.rfile.read(len).decode('utf-8'))
        self.send_response(200)
        self.send_header(b'Content-type', b'text/plain')
        self.end_headers()
        self.wfile.write("In the JSON you sent me, data['foo'][2] is {}\n".format(data['text'][2]).encode('utf-8'))

server = HTTPServer(('localhost', 2000), ExampleJSONHandler)
server.serve_forever()