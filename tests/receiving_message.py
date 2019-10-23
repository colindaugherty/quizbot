from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib
import urllib2
import json

class ExampleJSONHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        len = int(self.headers.get('Content-Length'))
        data = json.loads(self.rfile.read(len).decode('utf-8'))
        self.send_response(200)
        self.send_header(b'Content-type', b'text/plain')
        self.end_headers()
        self.wfile.write("In the JSON you sent me, data['foo'][2] is {}\n".format(data['text'][2]).encode('utf-8'))
        message = "This is the message I received {}\n".format(data['text'])

        data = {"bot_id": self.bot_id, "text": str(message)}
        req = urllib2.Request('https://api.groupme.com/v3/bots/post')
        req.add_header('Content-Type', 'application/json')

        response = urllib2.urlopen(req, json.dumps(data))
        response.close()

server = HTTPServer(("192.168.0.69", 2000), ExampleJSONHandler)
server.serve_forever()
