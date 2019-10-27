#this is just me figuring out how the server and all that worked
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import requests
import re

url = "https://api.groupme.com/v3/bots/post"

meme_regex = re.compile("(!meme)")

class ExampleJSONHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        len = int(self.headers.get('Content-Length'))
        data = json.loads(self.rfile.read(len).decode('utf-8'))
        self.send_response(200)
        self.send_header(b'Content-type', b'text/plain')
        self.end_headers()
        if data['name'] != "test beep boop":
            self.wfile.write("In the JSON you sent me, data['foo'][2] is {}\n".format(data['text'][2]).encode('utf-8'))
            if meme_regex.match(data['text']) != None:
                message = "You just asked me for a meme but I can't do that yet :'("
                data = {"bot_id": "31283ec6a67b96f542641a4aa9", "text": str(message)}
                r = requests.post(url, json=data)
                self.wfile.write("\nThis is the post request I just tried-\n")
                self.wfile.write(r.text)
                self.wfile.write("\n")
            else:
                message = "This is the message I received: {}\n".format(data['text'])
                data = {"bot_id": "31283ec6a67b96f542641a4aa9", "text": str(message)}
                r = requests.post(url, json=data)
                self.wfile.write("\nThis is the post request I just tried-\n")
                self.wfile.write(r.text)
                self.wfile.write("\n")

server = HTTPServer(("192.168.0.69", 2000), ExampleJSONHandler)
server.serve_forever()
