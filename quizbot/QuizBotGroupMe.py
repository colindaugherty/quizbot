# fair warning to y'all. this is gonna be wack
# it is very wack
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, requests, re, time, os, random, logging, sqlite3
from .message_routing import GroupMeMessageRouter

# main functions
from .modules.QuizBotSendRedditMeme import QuizBotSendRedditMeme
from .modules.QuizBotSendInstaMeme import QuizBotSendInstaMeme
from .modules.QuizBotFunSayings import QuizBotFunSayings
from .modules.QuizBotHackingJoke import QuizBotHackingJoke
from .modules.QuizBotHelp import QuizBotHelp
from .modules.QuizBotQuizzer import QuizBotQuizzer

# config functions - database manipulation
from .modules.QuizBotUpdateConfig import QuizBotUpdateConfig
from .modules.QuizBotSetMemeSource import QuizBotSetMemeSource

logging.basicConfig(level=logging.DEBUG,filename='access.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

conn = sqlite3.connect('config.db')

logging.info("Started program. Hello world!")

config_file = os.path.join('.', 'data', 'config.json')
quiz_file = os.path.join('.', 'data', 'quiz_material.json')

class QuizBotGroupMe():
    def __init__(self, bot_id):
        # grab config from files
        with open(config_file) as data_file:
            config = json.load(data_file)

        with open(quiz_file) as data_file:
            self.quizmaterial = json.load(data_file)

        # start bot variables
        self.bots = config['bots']
        reallist = []
        for bot in self.bots:
            bot = tuple(bot)
            logging.info("Found bot- {}".format(bot))
            reallist.append(bot)
        self.bots = reallist
        self.listening_port = config['listening_port']
        self.groupme_url = "https://api.groupme.com/v3/bots/post"

        self.useReddit = True

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
            c.execute("SELECT * FROM config WHERE name=? AND botid=? AND groupid=?", iteration_values)
            databasecheckconfig = c.fetchone()
            c.execute("SELECT * FROM memesource WHERE name=? AND botid=? AND groupid=?", iteration_values)
            databasecheckmemesource = c.fetchone()
            if databasecheckconfig == None and databasecheckmemesource == None or None in databasecheckconfig and None in databasecheckmemesource:
                logging.info(f"Doing default config for bot {name} (id#{id} and groupid#{group})")
                insertvalues = [(name, id, group, 'false','false')]
                c.executemany("INSERT INTO config (name, botid, groupid, allownsfw, allowrepost) VALUES (?,?,?,?,?)", insertvalues)
                insertvalues = [(name, id, group, 'all')]
                c.executemany("INSERT INTO memesource (name, botid, groupid, subreddit) VALUES (?,?,?,?)", insertvalues)
                logging.info("Finished - results:\n")
                for row in c.execute("SELECT * FROM config ORDER BY id"):
                    logging.info(row)
                for row in c.execute("SELECT * FROM memesource ORDER BY botid"):
                    logging.info(row)
                conn.commit()
            else:
                for row in c.execute("SELECT * FROM config ORDER BY id"):
                    logging.info(row)
                for row in c.execute("SELECT * FROM memesource ORDER BY botid"):
                    logging.info(row)
        conn.commit()
        conn.close()

        # all finished here, init regex time now
        self._init_regexes()
    
    def _init_regexes(self):
        self.likes = re.compile("(^!likes$)")
        self.likesrank = re.compile("(^!rank$)")
        self.randommeme = re.compile("(^!meme$)")
        self.groupinfo = re.compile("(^!info$)")
        self.help_regex = re.compile("(^!help$)")
        self.config = re.compile("(^!config)")
        self.authenticate = re.compile("(^!authenticate)")
        self.quiz = re.compile("(^!quiz)")
        self.hacking_joke = re.compile("(^!hack)")
        self.fred_joke = re.compile("(^!fred)")

        self._construct_regexes()

    def _construct_regexes(self):
        self.regex_actions = [
            ("Likes", self.likes, self.send_likes),
            ("Rank", self.likesrank, self.send_rank),
            ("Meme", self.randommeme, self.send_meme),
            ("Info", self.groupinfo, self.send_info),
            ("Help", self.help_regex, self.send_help),
            ("Config", self.config, self.update_config),
            ("Authenticate", self.authenticate, self._authenticateUser),
            ("Quiz", self.quiz, self.quizzer),
            ("Joke/EasterEgg", self.hacking_joke, self.hack_joke),
            ("Joke/EasterEgg", self.fred_joke, self.fred_function)
        ]
        logging.info("Initialized regex.")

    def _authenticateUser(self, mes, att, type, text, sender_name):
        sender_name = sender_name.lower()
        sender_name = sender_name.replace(" ", "_")
        logging.info(f"Sender name is - {sender_name}")
        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        text = text.lower()
        text = text.split()
        t = (self.bot_id, self.group_id)
        c.execute("SELECT users FROM authenticate WHERE (botid=? AND groupid=?)", (t))
        authenticatedCheck = c.fetchone()
        localusers = []
        if 0 <= 2 < len(text) and authenticatedCheck == None or 0 <= 2 < len(text) and None in authenticatedCheck:
            if text[1] == str(self.bot_name) and text[2] == str(self.group_id):
                if text[1] not in self.authenticatedUsers:
                    insertvalues = [(self.bot_name, self.bot_id, self.group_id, sender_name)]
                    c.executemany("INSERT INTO authenticate (name, botid, groupid, users) VALUES (?,?,?,?)", insertvalues)
                    for row in c.execute("SELECT users FROM authenticate WHERE (botid=? AND groupid=?)", (t)):
                        localusers.append(row[0])
                    logging.info(localusers)
                    conn.commit()
                    conn.close()
                    logging.info("Just authenticated a user, an updated list should be above me")
                    message = sender_name
                    message += " is now authenticated."
                    self.send_message(message, 1)
                else:
                    self.send_message("Error - user already authenticated", 1)
            else:
                self.send_message("Include bot_id and group_id.", 1)
        elif sender_name in self.authenticatedUsers:
            if 0 <= 1 < len(text):
                if text[1] not in self.authenticatedUsers:
                    insertvalues = [(self.bot_name, self.bot_id, self.group_id, text[1])]
                    c.executemany("INSERT INTO authenticate (name, botid, groupid, users) VALUES (?,?,?,?)", insertvalues)
                    for row in c.execute("SELECT users FROM authenticate WHERE (botid=? AND groupid=?)", (t)):
                        localusers.append(row[0])
                    logging.info(localusers)
                    conn.commit()
                    conn.close()
                    logging.info("Just authenticated a user, an updated list should be above me")
                    message = "Authenticating user "
                    message += text[1]
                    message += " they will now have access to all commands."
                    self.send_message(message, 1)
                else:
                    self.send_message("Error - user is already authenticated.", 1)
        else:
            self.send_message("I'm sorry, but you can not authenticate anyone :/", 1)

    def _getmemesource(self):
        x = QuizBotSetMemeSource(self.bot_id, self.group_id)
        return x.response

    def _getallownsfw(self):
        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        t = (self.bot_id, self.group_id)
        c.execute("SELECT allownsfw FROM config WHERE (botid=? AND groupid=?)", (t))
        allownsfw = c.fetchone()
        allownsfw = allownsfw[0]
        conn.commit()
        conn.close()
        return allownsfw

    def _getallowreposts(self):
        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        t = (self.bot_id, self.group_id)
        c.execute("SELECT allowrepost FROM config WHERE (botid=? AND groupid=?)", (t))
        allowrepost = c.fetchone()
        allowrepost = allowrepost[0]
        conn.commit()
        conn.close()
        return allowrepost

    def _getauthenticatedusers(self):
        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        t = (self.bot_id, self.group_id)
        users = []
        for row in c.execute("SELECT users FROM authenticate WHERE (botid=? AND groupid=?)", (t)):
            users.append(row[0])
        logging.info(f"Current authenticated users {users}")
        conn.commit()
        conn.close()
        return users

    def _init_config(self, groupid, bot_id, botname):
        self.bot_id = bot_id
        self.group_id = groupid
        self.meme_source = self._getmemesource()
        self.real_len = len(self.meme_source) - 1
        self.allow_nsfw = self._getallownsfw()
        self.allow_reposts = self._getallowreposts()
        self.bot_name = botname
        self.authenticatedUsers = self._getauthenticatedusers()
        logging.info(f"\n\n\nLOTS OF SPACE FOR CONFIG INITS\n\nTHESE ARE CONFIG VALUES-\n\nbot_id: {self.bot_id}\nmeme_source: {self.meme_source}\nallow_nsfw: {self.allow_nsfw}\nallow_reposts: {self.allow_reposts}\nbot_name: {self.bot_name}\ngroup_id: {self.group_id}\nauthenticatedUsers: {self.authenticatedUsers}\n\n\nEND CONFIG VALUES\n\n\n")
        logging.info("Initialized config for group %s" % (groupid))
        logging.info(f'Variables are -\nbot_id : {self.bot_id}\nlistening_port : {self.listening_port}\nmeme_source : {self.meme_source}')

    def receive_message(self, message, attachments, groupid, sendertype, sender_name):
        logging.info("\n\n\n\n\nreceived message from group: %s\nself.bots: %s\n\n\n\n" % (groupid, self.bots))
        if sendertype != "bot":
            if self.awaiting_response == False:
                for type, regex, action in self.regex_actions:
                    mes = regex.match(message)
                    att = attachments
                    gid = groupid
                    for name, id, group in self.bots:
                        if group != gid:
                            logging.info("%s and id#%s matched group id#%s" % (name, id, gid))
                            bot_id = id
                            gid = int(gid)
                            botname = name
                            self._init_config(gid, bot_id, botname)
                        else:
                            logging.info("%s and id#%s did not match group id#%s" %(name, id, gid))
                    if mes:
                        logging.info(f'Received message with type:{type} and message:{mes}\nfrom group:{gid} so bot {botname} should reply')
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
        self.send_message("Unfortunately, %s, this is not currently working. Stay tuned!" % (sender_name), 1)

    def send_info(self, mes, att, gid, text, sender_name):
        self.send_message("Unfortunately, %s, this is not currently working. Stay tuned!" % (sender_name), 1)

    def send_rank(self, mes, att, gid, text, sender_name):
        self.send_message("Unfortunately, %s, this is not currently working. Stay tuned!" % (sender_name), 1)

    def quizzer(self, mes, att, gid, text, sender_name):
        if self.awaiting_response == False:
            self.quizzerbot = QuizBotQuizzer(self.authenticatedUsers, sender_name, self.quizbonuses)
            self.quizzerbot.start_quiz(text)
            self.send_message(self.quizzerbot.response, 1)
            self.awaiting_response = self.quizzerbot.awaiting_response 
        elif self.awaiting_response == True:
            self.quizzerbot.continue_quiz(text, sender_name)
            if self.quizzerbot.goodjob:
                self.send_message(self.quizzerbot.goodjob, 1)
            if self.quizzerbot.finishedQuiz == False and self.quizzerbot.correct == True:
                self.send_message(self.quizzerbot.response, 5)
            elif self.quizzerbot.finishedQuiz == True:
                self.send_message("Finished quiz! Generating results", 1)
                self.send_message(self.quizzerbot.response, 1)
            else:
                logging.info("Finished quiz is broken, error")
            self.awaiting_response = self.quizzerbot.awaiting_response

    def update_config(self, mes, att, gid, text, sender_name):
        x = QuizBotUpdateConfig(self.authenticatedUsers, self.bot_name, self.bot_id, self.group_id, sender_name, self.allow_nsfw, self.allow_reposts, self.meme_source, text)
        self.send_message(x.response, 1)
        
    def send_meme(self, mes, att, gid, text, sender_name):
        if self.useReddit == True:
            x = QuizBotSendRedditMeme(self.meme_source, self.real_len)
        elif self.useReddit == False:
            x = QuizBotSendInstaMeme(self.meme_source, self.real_len)
        self.send_message(x.response, 1)

    def send_help(self, mes, att, gid, text, sender_name):
        x = QuizBotHelp()
        self.send_message(x.response, 1)

    def hack_joke(self, mes, att, type, text, sender_name):
        x = QuizBotHackingJoke(self.group_id, sender_name)
        self.send_message(x.response, 1)
    
    def fred_function(self, mes, att, type, text, sender_name):
        x = QuizBotFunSayings(sender_name)
        self.send_message(x.response, 1)

    def send_message(self, message, t):
        data = {"bot_id": self.bot_id, "text": str(message)}
        time.sleep(t)
        requests.post(self.groupme_url, json=data)
        logging.info(f"Just sent a message-\n{message}\n")

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