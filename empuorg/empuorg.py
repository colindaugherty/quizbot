# fair warning to y'all. this is gonna be wack
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, requests, re, time, os, random, praw
from .message_routing import MessageRouter

reddit = praw.Reddit(client_id="nothing, don't hack me", client_secret="nothing", user_agent="nothing")
config_file = os.path.join('.', 'data', 'config.json')

class Empuorg():
    def __init__(self, bot_id):
        with open(config_file) as data_file:
            config = json.load(data_file)

        self.bot_id = config['bot_id']
        print(self.bot_id)
        self.meme_source = config['meme_source']
        print(self.meme_source)
        self.listening_port = config['listening_port']
        print(self.listening_port)
        self.groupme_url = "https://api.groupme.com/v3/bots/post"

        self._init_regexes()
    
    def _init_regexes(self):
        self.likes = re.compile("(!likes)")
        self.likesrank = re.compile("(!rank)")
        self.randommeme = re.compile("(!meme)")
        self.groupinfo = re.compile("(!info)")
        self.help_regex = re.compile("(!help)")

        self._construct_regexes()
    
    def _construct_regexes(self):
        self.regex_actions = [
            ("Likes", self.likes, self.send_likes),
            ("Rank", self.likesrank, self.send_rank),
            ("Meme", self.randommeme, self.send_meme),
            ("Info", self.groupinfo, self.send_info),
            ("Help", self.help_regex, self.send_help)
        ]

    def receive_message(self, message, attachments, senderid):
        for type, regex, action in self.regex_actions:
            mes = regex.match(message)
            att = attachments
            sid = senderid
            if mes:
                print("Received a message- %s\nType of request is- %s" % (mes, type))
                if att:
                    action(mes, att, sid, message)
                else:
                    att = []
                    action(mes, att, sid, message)
                break
    
    def send_likes(self, mes, att, sid, text):
        self.send_message("Unfortunately, %s this is not currently working. Stay tuned!" % (sid))

    def send_info(self, mes, att, sid, text):
        self.send_message("Unfortunately, %s this is not currently working. Stay tuned!" % (sid))

    def send_rank(self, mes, att, sid, text):
        self.send_message("Unfortunately, %s this is not currently working. Stay tuned!" % (sid))

    def send_meme(self, mes, att, sid, text):
        rand = random.randint(0, len(self.meme_source))
        subreddit = self.meme_source[rand]
        submission_list = []
        for submission in reddit.subreddit(subreddit).hot(limit=3):
            submission_list.append(submission)
            print(submission)
        print(submission_list)


    def send_help(self, mes, att, sid, text):
        help_message = "Empuorg Bot Commands-\n"
        help_message += "Version 0.1b\n"
        help_message += "!memes - searches for a random meme from your meme suppliers in the config\n"
        help_message += "!info - prints information for the group\n"
        help_message += "!config - edits group config\n"
        help_message += "!help or ! - displays help commands\n"

        self.send_message(help_message)
    
    def send_message(self, message):
        data = {"bot_id": self.bot_id, "text": str(message)}
        time.sleep(1)
        r = requests.post(self.groupme_url, json=data)
        print("Just sent message with this text - ")
        print(r.text)

def init(bot_id=0):
    global bot
    bot = Empuorg(bot_id=bot_id)
    return bot

def listen(server_class=HTTPServer, handler_class=MessageRouter, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()