from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib
import json
import requests

url = "https://api.groupme.com/v3/bots/post"

class ExampleJSONHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        len = int(self.headers.get('Content-Length'))
        data = json.loads(self.rfile.read(len).decode('utf-8'))
        self.send_response(200)
        self.send_header(b'Content-type', b'text/plain')
        self.end_headers()
        self.wfile.write("In the JSON you sent me, data['foo'][2] is {}\n".format(data['text'][2]).encode('utf-8'))
        message = "This is the message I received {}\n".format(data['text'])

        data = {"bot_id": "31283ec6a67b96f542641a4aa9", "text": str(message)}
        r = requests.post(url, json=data)
        self.wfile.write("\nThis is the post request I just tried-\n")
        self.wfile.write(r.text)
        self.wfile.write("\n")

server = HTTPServer(("192.168.0.69", 2000), ExampleJSONHandler)
server.serve_forever()
