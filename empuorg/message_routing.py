from http.server import BaseHTTPRequestHandler
import json
import empuorg.empuorg as empuorg

class MessageRouter(BaseHTTPRequestHandler):

    def do_POST(self):
        content_len = int(self.headers['content-length'])
        post_body = self.rfile.read(content_len)
        data = json.loads(post_body)
        
        #when a request is recieved, process the response as JSON and pass relevant data to exbot class
        empuorg.bot.receive_message(data['text'],data['attachments'],data['sender_id'])