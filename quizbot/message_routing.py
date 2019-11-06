from http.server import BaseHTTPRequestHandler
import json


class GroupMeMessageRouter(BaseHTTPRequestHandler):

    def do_POST(self):
        import quizbot.QuizBotGroupMe as QuizBotGroupMe
        content_len = int(self.headers['content-length'])
        post_body = self.rfile.read(content_len)
        data = json.loads(post_body)
        print(data)
    
        QuizBotGroupMe.bot.receive_message(data['text'],data['attachments'],data['group_id'],data['sender_type'], data['name'])
