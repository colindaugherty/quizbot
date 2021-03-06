# fair warning to y'all. this is gonna be wack
# it is very wack
# group-me wrapper for quizbot

from http.server import HTTPServer, BaseHTTPRequestHandler
import json, requests, re, time, os, random, logging, sqlite3
from .message_routing import GroupMeMessageRouter

from .QuizBotDataHandler import QuizBotDataHandler

# main functions
from .modules.QuizBotSendRedditMeme import QuizBotSendRedditMeme
from .modules.QuizBotSendInstaMeme import QuizBotSendInstaMeme
from .modules.QuizBotFunSayings import QuizBotFunSayings
from .modules.QuizBotHackingJoke import QuizBotHackingJoke
from .modules.QuizBotHelp import QuizBotHelp
from .modules.QuizBotQuizzer import QuizBotQuizzer
from .modules.QuizBotReturnStats import QuizBotReturnStats

# config functions - database manipulation
from .modules.QuizBotUpdateConfig import QuizBotUpdateConfig
from .modules.QuizBotSetMemeSource import QuizBotSetMemeSource
from .modules.QuizBotOptIO import QuizBotOptIO
from .modules.QuizBotAuthenticateUser import QuizBotAuthenticateUser

datahandler = QuizBotDataHandler(groupme=True)

groupmelogger = logging.getLogger(__name__)

# groupmelogger.basicConfig(level=logging.DEBUG,filename='logs/groupme.log', filemode='w', format='QuizBot[GROUPME]: %(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

groupmelogger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('logs/groupme.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('QuizBot[GROUPME]: %(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the file handler to the logger
groupmelogger.addHandler(handler)

conn = sqlite3.connect('config.db')

groupmelogger.info("Started program. Hello world!")

config_file = os.path.join('.', 'data', 'config.json')

class QuizBotGroupMe():
    def __init__(self, bot_id):
        self.newsroom_people = ["Chris Dowdy", "Jackson Powell", "Kali Knight", "Bailee T. Hertrick"]

        # grab config from files
        with open(config_file) as data_file:
            config = json.load(data_file)

        # start bot variables
        self.bots = config['bots']
        reallist = []
        for bot in self.bots:
            bot = tuple(bot)
            groupmelogger.info("Found bot- {}".format(bot))
            reallist.append(bot)
        self.bots = reallist
        self.listening_port = config['listening_port']
        self.groupme_url = "https://api.groupme.com/v3/bots/post"

        self.useReddit = False

        # quizzing variables
        self.awaiting_response = False
        self.quizbonuses = False
        
        # initializing database defaults for any new bots
        for name, id, group in self.bots:
            iteration_values = (name, id, group)
            c = conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS config
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, botid text, groupid int, allownsfw text, allowrepost text)
            """)
            c.execute("""CREATE TABLE IF NOT EXISTS memesource
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, botid text, groupid int, subreddit text)
            """)
            c.execute("""CREATE TABLE IF NOT EXISTS authenticate
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, botid text, groupid int, users text)
            """)
            c.execute("""CREATE TABLE IF NOT EXISTS opt
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, botid text, groupid int, users text, newsroom text, elimination text)
            """)
            c.execute("""CREATE TABLE IF NOT EXISTS stats
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, botid text, groupid int, requests int, responses int, FredResponses int, TotalMessages int)
            """)
            c.execute("SELECT * FROM config WHERE name=? AND botid=? AND groupid=?", iteration_values)
            databasecheckconfig = c.fetchone()
            c.execute("SELECT * FROM memesource WHERE name=? AND botid=? AND groupid=?", iteration_values)
            databasecheckmemesource = c.fetchone()
            c.execute("SELECT * FROM stats WHERE name=? AND botid=? AND groupid=?", iteration_values)
            databasecheckstats = c.fetchone()
            if databasecheckstats == None or None in databasecheckstats:
                groupmelogger.info(f"Setting up default stats for bot {name} (id#{id} and groupid#{group})")
                insertvalues = [(name, id, group, 0, 0, 0, 0)]
                c.executemany("INSERT INTO stats (name, botid, groupid, requests, responses, FredResponses, TotalMessages) VALUES (?, ?, ?, ?, ?, ?, ?)", insertvalues)
                for row in c.execute("SELECT * FROM stats ORDER BY botid"):
                    groupmelogger.info(row)
                conn.commit()
            else:
                for row in c.execute("SELECT * FROM stats ORDER BY botid"):
                    groupmelogger.info(row)
            if databasecheckconfig == None and databasecheckmemesource == None or None in databasecheckconfig and None in databasecheckmemesource:
                groupmelogger.info(f"Doing default config for bot {name} (id#{id} and groupid#{group})")
                insertvalues = [(name, id, group, 'false','false')]
                c.executemany("INSERT INTO config (name, botid, groupid, allownsfw, allowrepost) VALUES (?,?,?,?,?)", insertvalues)
                insertvalues = [(name, id, group, 'all')]
                c.executemany("INSERT INTO memesource (name, botid, groupid, subreddit) VALUES (?,?,?,?)", insertvalues)
                groupmelogger.info("Finished - results:\n")
                for row in c.execute("SELECT * FROM config ORDER BY id"):
                    groupmelogger.info(row)
                for row in c.execute("SELECT * FROM memesource ORDER BY botid"):
                    groupmelogger.info(row)
                conn.commit()
            else:
                for row in c.execute("SELECT * FROM config ORDER BY id"):
                    groupmelogger.info(row)
                for row in c.execute("SELECT * FROM memesource ORDER BY botid"):
                    groupmelogger.info(row)
        conn.commit()
        conn.close()

        # all finished here, init regex time now
        self._init_regexes()
    
    def _init_regexes(self):
        self.likes = re.compile("(^!likes$)")
        self.likesrank = re.compile("(^!rank$)")
        self.randommeme = re.compile("(^!meme$)")
        self.groupinfo = re.compile("(^!info$)")
        self.stats = re.compile("(^!stats$)")
        self.help_regex = re.compile("(^!help)")
        self.config = re.compile("(^!config)")
        self.authenticate = re.compile("(^!authenticate)")
        self.deauthenticate = re.compile("(^!deauthenticate)")
        self.quiz = re.compile("(^!quiz)")
        self.hacking_joke = re.compile("(^!hack)")
        self.fred_joke = re.compile("(^!fred)")
        self.optregex = re.compile("(^!opt)")
        self.newsroom = re.compile("(^!newsroom)")

        self._construct_regexes()

    def _construct_regexes(self):
        self.regex_actions = [
            ("Likes", self.likes, self.send_likes),
            ("Rank", self.likesrank, self.send_rank),
            ("Meme", self.randommeme, self.send_meme),
            ("Info", self.groupinfo, self.send_info),
            ("Info", self.stats, self.send_info),
            ("Help", self.help_regex, self.send_help),
            ("Config", self.config, self.update_config),
            ("Authenticate", self.authenticate, self._authenticateUser),
            ("Authenticate", self.deauthenticate, self._authenticateUser),
            ("Quiz", self.quiz, self.quizzer),
            ("Joke/EasterEgg", self.hacking_joke, self.hack_joke),
            ("Joke/EasterEgg", self.fred_joke, self.fred_function),
            ("Opting In/Out", self.optregex, self.opt),
            ("Newsroom", self.newsroom, self.newsroom_selection)
        ]
        groupmelogger.info("Initialized regex.")

    def _authenticateUser(self, mes, att, type, text, sender_name):
        x = QuizBotAuthenticateUser(sender_name, text, self.bot_name, self.group_id, datahandler)
        self.send_message(x.response, 1)

    def _getmemesource(self):
        x = QuizBotSetMemeSource(self.bot_id, self.group_id)
        return x.response

    def _getallownsfw(self):
        data = {"name" : self.bot_name, "groupid" : self.group_id, "table" : ["config", "allownsfw"], "data" : [self.bot_name, self.group_id]}
        allownsfw = datahandler.do("selectone", data)
        return allownsfw

    def _getallowreposts(self):
        data = {"name" : self.bot_name, "groupid" : self.group_id, "table" : ["config", "allowrepost"], "data" : [self.bot_name, self.group_id]}
        allowrepost = datahandler.do("selectone", data)
        return allowrepost

    def _getauthenticatedusers(self):
        data = {"name" : self.bot_name, "groupid" : self.group_id, "table" : "authenticate", "data" : [self.bot_name, self.group_id]}
        users = datahandler.do("select", data)
        return users

    def _init_config(self, groupid, bot_id, botname):
        self.bot_id = bot_id
        self.group_id = groupid
        self.bot_name = botname
        self.meme_source = self._getmemesource()
        self.real_len = len(self.meme_source) - 1
        self.allow_nsfw = self._getallownsfw()
        self.allow_reposts = self._getallowreposts()
        self.authenticatedUsers = self._getauthenticatedusers()
        groupmelogger.info(f"\n\n\nLOTS OF SPACE FOR CONFIG INITS\n\nTHESE ARE CONFIG VALUES-\n\nbot_id: {self.bot_id}\nmeme_source: {self.meme_source}\nallow_nsfw: {self.allow_nsfw}\nallow_reposts: {self.allow_reposts}\nbot_name: {self.bot_name}\ngroup_id: {self.group_id}\nauthenticatedUsers: {self.authenticatedUsers}\n\n\nEND CONFIG VALUES\n\n\n")
        groupmelogger.info("Initialized config for group %s" % (groupid))
        groupmelogger.info(f'Variables are -\nbot_id : {self.bot_id}\nlistening_port : {self.listening_port}\nmeme_source : {self.meme_source}')

    def receive_message(self, message, attachments, groupid, sendertype, sender_name):
        groupmelogger.info("\n\n\n\n\nreceived message from group: %s\nself.bots: %s\n\n\n\n" % (groupid, self.bots))
        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        group = int(groupid)
        t = [(group)]
        groupmelogger.info(t)
        c.execute("UPDATE stats SET TotalMessages = TotalMessages + 1 WHERE (groupid=?)", t)
        conn.commit()
        conn.close()
        message = message.strip()
        if sendertype != "bot":
            if self.awaiting_response == False:
                for type, regex, action in self.regex_actions:
                    mes = regex.match(message)
                    att = attachments
                    gid = groupid
                    for name, id, group in self.bots:
                        if group == gid:
                            groupmelogger.info("%s and id#%s matched group id#%s" % (name, id, gid))
                            bot_id = id
                            gid = int(gid)
                            botname = name
                            self._init_config(gid, bot_id, botname)
                        else:
                            groupmelogger.info("%s and id#%s did not match group id#%s" %(name, id, gid))
                    if mes:
                        groupmelogger.info(f'Received message with type:{type} and message:{mes}\nfrom group:{gid} so bot {botname} should reply')
                        if att:
                            action(mes, att, gid, message, sender_name)
                        else:
                            att = []
                            action(mes, att, gid, message, sender_name)
            elif self.awaiting_response == True:
                mes = "none"
                att = attachments
                gid = groupid
                self.quizzer(mes, att, gid, message, sender_name)
            else:
                self.send_message("Error - awaiting_response is broken, setting it to False in order to avoid an infinite loop", 1)
                self.awaiting_response = False
    
    def send_likes(self, mes, att, gid, text, sender_name):
        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        t = [(self.bot_name, self.bot_id, self.group_id)]
        c.executemany("UPDATE stats SET requests = requests + 1 WHERE (name=? AND botid=? AND groupid=?)", t)
        c.executemany("UPDATE stats SET responses = responses + 1 WHERE (name=? AND botid=? AND groupid=?)", t)
        conn.commit()
        conn.close()
        self.send_message("Unfortunately, %s, this is not currently working. Stay tuned!" % (sender_name), 1)

    def send_info(self, mes, att, gid, text, sender_name):
        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        t = [(self.bot_name, self.bot_id, self.group_id)]
        c.executemany("UPDATE stats SET requests = requests + 1 WHERE (name=? AND botid=? AND groupid=?)", t)
        c.executemany("UPDATE stats SET responses = responses + 1 WHERE (name=? AND botid=? AND groupid=?)", t)
        conn.commit()
        conn.close()
        x = QuizBotReturnStats(self.bot_name, self.group_id)
        self.send_message(x.response, 1)

    def send_rank(self, mes, att, gid, text, sender_name):
        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        t = [(self.bot_name, self.bot_id, self.group_id)]
        c.executemany("UPDATE stats SET requests = requests + 1 WHERE (name=? AND botid=? AND groupid=?)", t)
        c.executemany("UPDATE stats SET responses = responses + 1 WHERE (name=? AND botid=? AND groupid=?)", t)
        conn.commit()
        conn.close()
        self.send_message("Unfortunately, %s, this is not currently working. Stay tuned!" % (sender_name), 1)

    def opt(self, mes, att, gid, text, sender_name):
        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        t = [(self.bot_name, self.bot_id, self.group_id)]
        c.executemany("UPDATE stats SET requests = requests + 1 WHERE (name=? AND botid=? AND groupid=?)", t)
        c.executemany("UPDATE stats SET responses = responses + 1 WHERE (name=? AND botid=? AND groupid=?)", t)
        conn.commit()
        conn.close()
        x = QuizBotOptIO(sender_name, text, self.group_id, self.bot_name, datahandler)
        self.send_message(x.response, 1)

    def quizzer(self, mes, att, gid, text, sender_name):
        if self.awaiting_response == False:
            conn = sqlite3.connect('config.db')
            c = conn.cursor()
            t = [(self.bot_name, self.bot_id, self.group_id)]
            c.executemany("UPDATE stats SET requests = requests + 1 WHERE (name=? AND botid=? AND groupid=?)", t)
            c.executemany("UPDATE stats SET responses = responses + 1 WHERE (name=? AND botid=? AND groupid=?)", t)
            conn.commit()
            conn.close()
            self.quizzerbot = QuizBotQuizzer(self.authenticatedUsers, sender_name, self.quizbonuses)
            self.quizzerbot.start_quiz(text)
            self.send_message(self.quizzerbot.response, 1)
            self.awaiting_response = self.quizzerbot.awaiting_response 
        elif self.awaiting_response == True:
            conn = sqlite3.connect('config.db')
            c = conn.cursor()
            t = [(self.bot_name, self.bot_id, self.group_id)]
            c.executemany("UPDATE stats SET responses = responses + 1 WHERE (name=? AND botid=? AND groupid=?)", t)
            conn.commit()
            conn.close()
            self.quizzerbot.continue_quiz(text, sender_name)
            if self.quizzerbot.goodjob:
                self.send_message(self.quizzerbot.goodjob, 1)
            if self.quizzerbot.finishedQuiz == False and self.quizzerbot.correct == True:
                self.send_message(self.quizzerbot.response, 5)
            elif self.quizzerbot.finishedQuiz == True:
                self.send_message("Finished quiz! Generating results", 1)
                self.send_message(self.quizzerbot.response, 1)
            elif self.quizzerbot.finishedQuiz != True and self.quizzerbot.finishedQuiz != False:
                groupmelogger.info("Finished quiz is broken, error")
            self.awaiting_response = self.quizzerbot.awaiting_response

    def update_config(self, mes, att, gid, text, sender_name):
        x = QuizBotUpdateConfig(self.authenticatedUsers, text, self.bot_name, self.group_id, sender_name, datahandler)
        self.send_message(x.response, 1)
        
    def send_meme(self, mes, att, gid, text, sender_name):
        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        t = [(self.bot_name, self.bot_id, self.group_id)]
        c.executemany("UPDATE stats SET requests = requests + 1 WHERE (name=? AND botid=? AND groupid=?)", t)
        c.executemany("UPDATE stats SET responses = responses + 1 WHERE (name=? AND botid=? AND groupid=?)", t)
        conn.commit()
        conn.close()
        if self.useReddit == True:
            x = QuizBotSendRedditMeme(self.meme_source, self.real_len)
        elif self.useReddit == False:
            x = QuizBotSendInstaMeme(self.meme_source, self.real_len)
        self.send_media(x.response, x.media, 1)

    def send_help(self, mes, att, gid, text, sender_name):
        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        t = [(self.bot_name, self.bot_id, self.group_id)]
        c.executemany("UPDATE stats SET requests = requests + 1 WHERE (name=? AND botid=? AND groupid=?)", t)
        c.executemany("UPDATE stats SET responses = responses + 1 WHERE (name=? AND botid=? AND groupid=?)", t)
        conn.commit()
        conn.close()
        x = QuizBotHelp(text)
        self.send_message(x.response, 1)

    def hack_joke(self, mes, att, type, text, sender_name):
        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        t = [(self.bot_name, self.bot_id, self.group_id)]
        c.executemany("UPDATE stats SET requests = requests + 1 WHERE (name=? AND botid=? AND groupid=?)", t)
        c.executemany("UPDATE stats SET responses = responses + 1 WHERE (name=? AND botid=? AND groupid=?)", t)
        conn.commit()
        conn.close()
        x = QuizBotHackingJoke(self.group_id, text, sender_name)
        self.send_message(x.response, 1)
    
    def fred_function(self, mes, att, type, text, sender_name):
        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        t = [(self.bot_name, self.bot_id, self.group_id)]
        c.executemany("UPDATE stats SET requests = requests + 1 WHERE (name=? AND botid=? AND groupid=?)", t)
        c.executemany("UPDATE stats SET responses = responses + 1 WHERE (name=? AND botid=? AND groupid=?)", t)
        c.executemany("UPDATE stats SET FredResponses = FredResponses + 1 WHERE (name=? AND botid=? AND groupid=?)", t)
        conn.commit()
        conn.close()
        x = QuizBotFunSayings(sender_name)
        self.send_message(x.response, 1)

    def newsroom_selection(self, mes, att, type, text, sender_name):
        self.send_message("Selecting people for newsroom...", 1)
        for person in self.newsroom_people:
            self.send_message(person, 3)
        self.send_message("Finished!\nHave fun!\n(if you have any questions ask Colin)", 1)

    def send_message(self, message, t):
        data = {"bot_id": self.bot_id, "text": str(message)}
        time.sleep(t)
        requests.post(self.groupme_url, json=data)
        groupmelogger.info(f"Just sent a message-\n{message}\n")

    def send_media(self, message, media, t):
        data = {"bot_id": self.bot_id, "text": str(message), "image_url": media}
        time.sleep(t)
        requests.post(self.groupme_url, json=data)
        groupmelogger.info(f"Just sent a message-\n{message}\n")

# init bot
def init(bot_id=0):
    global bot
    bot = QuizBotGroupMe(bot_id=bot_id)
    return bot


# listen and send all messages to the message router
def listen(server_class=HTTPServer, handler_class=GroupMeMessageRouter, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()