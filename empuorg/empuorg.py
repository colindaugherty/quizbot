# fair warning to y'all. this is gonna be wack
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, requests, re, time, os, random, praw, logging, sqlite3
from .message_routing import MessageRouter

logging.basicConfig(level=logging.DEBUG,filename='access.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

conn = sqlite3.connect('config.db')

logging.info("Started program. Hello world!")

reddit = praw.Reddit(client_id="pPp18DiGR-UnFA", client_secret="vmY57gKz-6l01ePkoC2FMmv1nv4", user_agent="groupmebot /u/b1ackzi0n")
config_file = os.path.join('.', 'data', 'config.json')

class Empuorg():
    def __init__(self, bot_id):
        with open(config_file) as data_file:
            config = json.load(data_file)

        self.bots = config['bots']
        reallist = []
        for bot in self.bots:
            bot = tuple(bot)
            print(bot)
            reallist.append(bot)
        self.bots = reallist
        print(self.bots)
        for name, id, group in self.bots:
            iteration_values = (name, id, group)
            c = conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS config
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, botid text, groupid text, allownsfw text, allowrepost text)
            """)
            c.execute("""CREATE TABLE IF NOT EXISTS memesource
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, botid text, groupid text, subreddit text)
            """)
            databasecheckconfig = c.execute("SELECT * FROM config WHERE name=? AND botid=? AND groupid=?", iteration_values)
            databasecheckmemesource = c.execute("SELECT * FROM memesource WHERE name=? AND botid=? AND groupid=?", iteration_values)
            if None in databasecheckconfig and None in databasecheckmemesource:
                print("Doing default config for bot %s (id#%s and groupid#%s)" % (name, id, group))
                insertvalues = [(name, id, group, 'false','false')]
                c.executemany("INSERT INTO config (name, botid, groupid, allownsfw, allowrepost) VALUES (?,?,?,?,?)", insertvalues)
                insertvalues = [(name, id, group, 'all')]
                c.executemany("INSERT INTO memesource (name, botid, groupid, subreddit) VALUES (?,?,?,?)", insertvalues)
                print("Finished - results:\n")
                for row in c.execute("SELECT * FROM config ORDER BY id"):
                    print(row)
                for row in c.execute("SELECT * FROM memesource ORDER BY botid"):
                    print(row)
                conn.commit()
            else:
                for row in c.execute("SELECT * FROM config ORDER BY id"):
                    print(row)
                for row in c.execute("SELECT * FROM memesource ORDER BY botid"):
                    print(row)
        conn.commit()
        conn.close()

        # self.bot_id = config['bot_id']
        # print(self.bot_id)
        # self.meme_source = config['meme_source']
        # print(self.meme_source)
        # self.real_len = len(self.meme_source) - 1
        self.listening_port = config['listening_port']
        print(self.listening_port)
        print(reddit.read_only)
        self.groupme_url = "https://api.groupme.com/v3/bots/post"

        self._init_regexes()
    
    def _init_regexes(self):
        self.likes = re.compile("(!likes)")
        self.likesrank = re.compile("(!rank)")
        self.randommeme = re.compile("(!meme)")
        self.groupinfo = re.compile("(!info)")
        self.help_regex = re.compile("(!help)")

        self._construct_regexes()
    
    def _init_config(self, groupid, bot_id, meme_source, allow_nsfw, allow_reposts):
        self.bot_id = bot_id
        self.meme_source = meme_source
        self.real_len = len(self.meme_source) - 1
        self.allow_nsfw = allow_nsfw
        self.allow_reposts = allow_reposts
        logging.info("Initialized config for group %s" % (groupid))
        logging.info(f'Variables are -\nbot_id : {self.bot_id}\nlistening_port : {self.listening_port}\nmeme_source : {self.meme_source}')

    def _construct_regexes(self):
        self.regex_actions = [
            ("Likes", self.likes, self.send_likes),
            ("Rank", self.likesrank, self.send_rank),
            ("Meme", self.randommeme, self.send_meme),
            ("Info", self.groupinfo, self.send_info),
            ("Help", self.help_regex, self.send_help)
        ]
        logging.info("Initialized regex.")

    def _getmemesource(self, id, group):
        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        values = [(id, group)]
        memesource = []
        for row in c.execute("SELECT subreddit FROM memesource WHERE id=? AND WHERE groupid=?", values):
            memesource.append(row)
        conn.commit()
        conn.close()
        return memesource

    def _getallownsfw(self, id, group):
        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        values = [(id, group)]
        for text in c.execute("SELECT allownsfw FROM config WHERE id=? AND WHERE groupid=?", values):
            allownsfw = text
        conn.commit()
        conn.close()
        return allownsfw

    def _getallowreposts(self, id, group):
        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        values = [(id, group)]
        for text in c.execute("SELECT allowrepost FROM config WHERE id=? AND WHERE groupid=?", values):
            allowrepost = text
        conn.commit()
        conn.close()
        return allowrepost

    def receive_message(self, message, attachments, groupid):
        for type, regex, action in self.regex_actions:
            mes = regex.match(message)
            att = attachments
            gid = groupid
            for name, id, group in self.bots:
                if group == gid:
                    # database functions return all the variables
                    bot_id = id
                    botname = name
                    meme_source = self._getmemesource(id, group)
                    allow_nsfw = self._getallownsfw(id, group)
                    allow_reposts = self._getallowreposts(id, group)
                    self._init_config(gid, bot_id, meme_source, allow_nsfw, allow_reposts)
                else:
                    print("%s and id#%s did not match group id#%s" %(name, id, gid))
            if mes:
                logging.info(f'Received message with type:{type} and message:{mes}\nfrom group:{gid} so bot {botname} should reply')
                if att:
                    action(mes, att, gid, message)
                else:
                    att = []
                    action(mes, att, gid, message)
                break
    
    def send_likes(self, mes, att, gid, text):
        self.send_message("Unfortunately, %s this is not currently working. Stay tuned!" % (gid))

    def send_info(self, mes, att, gid, text):
        self.send_message("Unfortunately, %s this is not currently working. Stay tuned!" % (gid))

    def send_rank(self, mes, att, gid, text):
        self.send_message("Unfortunately, %s this is not currently working. Stay tuned!" % (gid))

    def send_meme(self, mes, att, gid, text):
        start = time.time()
        meme_message = "Meme response-\n'"
        rand = random.randint(0, self.real_len)
        subreddit = self.meme_source[rand]
        submission_list = []
        for submission in reddit.subreddit(subreddit).hot(limit=10):
            if submission.stickied != True:
                submission_list.append(submission)
            else:
                print("We don't approve of stickied messages")
        submission_list_length = len(submission_list) - 1
        rand = random.randint(0,submission_list_length)
        print("Got a random submission index of %d out of %d\nIt has an upvote ratio of %d" % (rand, submission_list_length, submission_list[rand].upvote_ratio))
        print("Printing url link for post '%s'-\n" % (submission_list[rand].title))
        if submission_list[rand].selftext == "":
            print(submission_list[rand].url)
            result = submission_list[rand].url
        else:
            print(submission_list[rand].shortlink)
            result = submission_list[rand].shortlink
        meme_message += submission_list[rand].title
        meme_message += "' from the subreddit '"
        meme_message += submission_list[rand].subreddit.display_name
        meme_message += "'\n"
        meme_message += result
        meme_message += "\nI hope you enjoy!\n"
        meme_message += "response_time: "
        response_time = time.time() - start
        if time.strftime("%S", time.gmtime(response_time)) == "00":
            meme_message += "< 0s"
        else:
            meme_message += time.strftime("%Ss", time.gmtime(response_time))

        self.send_message(meme_message)


    def send_help(self, mes, att, gid, text):
        help_message = "Empuorg Bot Commands-\n"
        help_message += "Version 0.1b\n"
        help_message += "!memes - searches for a random meme from your meme suppliers in the config\n"
        help_message += "!info - prints information for the group\n"
        help_message += "!config - edits group config\n"
        help_message += "!help - displays help commands\n"

        self.send_message(help_message)
    
    def send_message(self, message):
        data = {"bot_id": self.bot_id, "text": str(message)}
        time.sleep(1)
        requests.post(self.groupme_url, json=data)
        logging.info(f"Just sent a message-\n{message}\n")

def init(bot_id=0):
    global bot
    bot = Empuorg(bot_id=bot_id)
    return bot

def listen(server_class=HTTPServer, handler_class=MessageRouter, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()