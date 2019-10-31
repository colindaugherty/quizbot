# fair warning to y'all. this is gonna be wack
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, requests, re, time, os, random, praw, logging, sqlite3
from .message_routing import MessageRouter

logging.basicConfig(level=logging.DEBUG,filename='access.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

conn = sqlite3.connect('config.db')

logging.info("Started program. Hello world!")

reddit = praw.Reddit(client_id="pPp18DiGR-UnFA", client_secret="vmY57gKz-6l01ePkoC2FMmv1nv4", user_agent="groupmebot /u/b1ackzi0n")
config_file = os.path.join('.', 'data', 'config.json')
quiz_file = os.path.join('.', 'data', 'quiz_material.json')

class Empuorg():
    def __init__(self, bot_id):
        with open(config_file) as data_file:
            config = json.load(data_file)

        with open(quiz_file) as data_file:
            self.quizmaterial = json.load(data_file)

        self.bots = config['bots']
        reallist = []
        for bot in self.bots:
            bot = tuple(bot)
            print(bot)
            reallist.append(bot)
        self.bots = reallist
        print(self.bots)
        self.awaiting_response = False
        self.current_quiz = []
        self.last_question = []
        self.quizbonuses = False
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
            print(databasecheckconfig)
            print(databasecheckmemesource)
            if databasecheckconfig == None and databasecheckmemesource == None or None in databasecheckconfig and None in databasecheckmemesource:
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

        self.listening_port = config['listening_port']
        print("Reddit read only is - " + reddit.read_only)
        self.groupme_url = "https://api.groupme.com/v3/bots/post"

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
            ("Quiz", self.quiz, self.start_quizzer)
        ]
        logging.info("Initialized regex.")

    def _authenticateUser(self, mes, att, type, text, sender_name):
        sender_name = sender_name.lower()
        sender_name = sender_name.replace(" ", "_")
        print(sender_name)
        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        text = text.lower()
        text = text.split()
        t = (self.bot_id, self.group_id)
        c.executemany("SELECT users FROM authenticate WHERE (botid=? AND groupid=?)", (t))
        authenticatedCheck = c.fetchone()
        print(authenticatedCheck)
        localusers = []
        if 0 <= 2 < len(text) and authenticatedCheck == None or 0 <= 2 < len(text) and None in authenticatedCheck:
            if text[1] == str(self.bot_name) and text[2] == str(self.group_id):
                if text[1] not in self.authenticatedUsers:
                    insertvalues = [(self.bot_name, self.bot_id, self.group_id, sender_name)]
                    c.executemany("INSERT INTO authenticate (name, botid, groupid, users) VALUES (?,?,?,?)", insertvalues)
                    for row in c.execute("SELECT users FROM authenticate WHERE (botid=? AND groupid=?)", (t)):
                        localusers.append(row[0])
                        print(row)
                    print(localusers)
                    conn.commit()
                    conn.close()
                    print("Just authenticated a user, an updated list should be above me")
                    message = sender_name
                    message += " is now authenticated."
                    self.send_message(message)
                else:
                    self.send_message("Error - user already authenticated")
            else:
                self.send_message("Include bot_id and group_id.")
        elif sender_name in self.authenticatedUsers:
            if 0 <= 1 < len(text):
                if text[1] not in self.authenticatedUsers:
                    insertvalues = [(self.bot_name, self.bot_id, self.group_id, text[1])]
                    c.executemany("INSERT INTO authenticate (name, botid, groupid, users) VALUES (?,?,?,?)", insertvalues)
                    for row in c.execute("SELECT users FROM authenticate WHERE (botid=? AND groupid=?)", (t)):
                        localusers.append(row[0])
                    print(localusers)
                    conn.commit()
                    conn.close()
                    print("Just authenticated a user, an updated list should be above me")
                    message = "Authenticating user "
                    message += text[1]
                    message += " they will now have access to all commands."
                    self.send_message(message)
                else:
                    self.send_message("Error - user is already authenticated.")
        else:
            self.send_message("I'm sorry, but you can not authenticate anyone :/")

    def _getmemesource(self):
        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        t = (self.bot_id, self.group_id)
        memesource = []
        for row in c.execute("SELECT subreddit FROM memesource WHERE (botid=? AND groupid=?)", (t)):
            memesource.append(row[0])
        print("Inside _getmemesource: memesource should be populated here it is- %s" % (memesource))
        conn.commit()
        conn.close()
        return memesource

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
        print("Current authenticated users %s" % (users))
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
        print("\n\n\nLOTS OF SPACE FOR CONFIG INITS\n\nTHESE ARE CONFIG VALUES-\n\nbot_id: %s\nmeme_source: %s\nallow_nsfw: %s\nallow_reposts: %s\nbot_name: %s\ngroup_id: %d\nauthenticatedUsers: %s\n\n\nEND CONFIG VALUES\n\n\n" % (self.bot_id, self.meme_source, self.allow_nsfw, self.allow_reposts, self.bot_name, self.group_id, self.authenticatedUsers))
        logging.info("Initialized config for group %s" % (groupid))
        logging.info(f'Variables are -\nbot_id : {self.bot_id}\nlistening_port : {self.listening_port}\nmeme_source : {self.meme_source}')

    def receive_message(self, message, attachments, groupid, sendertype, sender_name):
        print("\n\n\n\n\nreceived message from group: %s\nself.bots: %s\n\n\n\n" % (groupid, self.bots))
        if sendertype != "bot":
            if self.awaiting_response == False:
                for type, regex, action in self.regex_actions:
                    mes = regex.match(message)
                    att = attachments
                    gid = groupid
                    for name, id, group in self.bots:
                        if group != gid:
                            print("%s and id#%s did not match group id#%s" %(name, id, gid))
                        else:
                            # database functions return all the variables
                            print("%s and id#%s matched group id#%s" % (name, id, gid))
                            bot_id = id
                            gid = int(gid)
                            botname = name
                            self._init_config(gid, bot_id, botname)
                    if mes:
                        logging.info(f'Received message with type:{type} and message:{mes}\nfrom group:{gid} so bot {botname} should reply')
                        if att:
                            action(mes, att, gid, message, sender_name)
                        else:
                            att = []
                            action(mes, att, gid, message, sender_name)
            elif self.awaiting_response == True:
                self.continue_quiz(mes, att, gid, message, sender_name)
            else:
                self.send_message("Error - awaiting_response is broken, closing program to prevent infinite loop")
                exit()
    
    def send_likes(self, mes, att, gid, text, sender_name):
        self.send_message("Unfortunately, %s this is not currently working. Stay tuned!" % (sender_name))

    def send_info(self, mes, att, gid, text, sender_name):
        self.send_message("Unfortunately, %s this is not currently working. Stay tuned!" % (sender_name))

    def send_rank(self, mes, att, gid, text, sender_name):
        self.send_message("Unfortunately, %s this is not currently working. Stay tuned!" % (sender_name))

    def start_quizzer(self, mes, att, gid, text, sender_name):
        counter = 0
        mes = mes.replace("!quiz ", "")
        print(mes)
        while counter < mes:
            sections = self.quizmaterial['acts']['sections']
            sections = sections.keys()
            sections_index = len(sections) - 1
            rand = random.randint(0,sections_index)
            quiz_section = sections[rand]
            print(quiz_section)
            verse = self.quizmaterial['acts']['sections'][quiz_section]
            verse = verse.keys()
            quiz_verse = verse[rand]
            print(quiz_verse)
            questions = self.quizmaterial['acts']['sections'][quiz_section][quiz_verse]
            questions = questions.keys()
            if self.quizbonuses == False:
                quiz_question = questions[rand]
                questions = self.quizmaterial['acts']['sections'][quiz_section][quiz_verse]
                quiz_questionanswer = questions.get(quiz_question)
                self.current_quiz = [quiz_section, quiz_verse, quiz_question, quiz_questionanswer]
            elif self.quizbonuses == True:
                pass
            else:
                pass
            if sections_index != len(sections) - 1:
                pass
            print(sections)
            counter += 1
        message = "Here is your question from the section {}: {} ({})".format(self.current_quiz[0], self.current_quiz[1], self.current_quiz[2])
        self.send_message(message)

    def continue_quiz(self, mes, att, gid, text, sender_name):
        response = mes.lower()
        if response == self.current_quiz[3]:
            message = "Good job {} you got that one right!".format(sender_name)
            self.awaiting_response = False
            self.send_message(message)
        else:
            message = "Sorry {}, the answer isn't '{}'".format(sender_name, mes)

    def update_config(self, mes, att, gid, text, sender_name):
        sender_name = sender_name.lower()
        sender_name = sender_name.replace(" ", "_")
        if sender_name in self.authenticatedUsers:
            conn = sqlite3.connect('config.db')
            c = conn.cursor()
            text = text.lower()
            print(mes)
            what_config = ['subreddit','allownsfw','allowrepost']
            text = text.split(' ')
            print(text)
            configword = text[1]
            if configword in what_config:
                if what_config[0] == configword:
                    if 0 <= 2 < len(text):
                        if text[2] == 'add':
                            if 0 <= 3 < len(text):
                                isString = isinstance(text[3], str)
                                t = [(self.bot_name, self.bot_id, self.group_id, text[3])]
                                c.executemany("INSERT INTO memesource (name, botid, groupid, subreddit) VALUES (?,?,?,?)", t)
                                memesource = []
                                t = [(self.bot_name),]
                                for row in c.execute("SELECT subreddit FROM memesource WHERE (name=?)", (t)):
                                    memesource.append(row)
                                print("Just updated memesource here it is- %s" % (memesource))    
                                conn.commit()
                                conn.close()
                                message = "Updated subreddit list, added - "
                                message += text[3]
                                self.send_message(message)
                            else:
                                self.send_message("You didn't include a subreddit!\nUsage - !config subreddit add <subreddit>")
                        elif text[2] == 'delete':
                            if 0 <= 3 < len(text):
                                isString = isinstance(text[3], str)
                                t = [(text[3],self.bot_name)]
                                c.executemany("DELETE FROM memesource WHERE (subreddit=? AND name=?)", (t))
                                memesource = []
                                t = [(self.bot_name),]
                                for row in c.execute("SELECT subreddit FROM memesource WHERE (name=?)", (t)):
                                    memesource.append(row[0])
                                print("Just updated memesource here it is- %s" % (memesource))    
                                conn.commit()
                                conn.close()
                                message = "Updated subreddit list, removed - "
                                message += text[3]
                                self.send_message(message)
                            else:
                                self.send_message("You didn't include a subreddit!\nUsage - !config subreddit add <subreddit>")
                        else:
                            self.send_message("Incorrect usage, expected add|delete\nUsage - !config subreddit <add|delete>")
                    else:
                        message = "Current enabled subreddits to pull from -"
                        for subreddit in self.meme_source:
                            message += "\n{}".format(subreddit)
                        self.send_message(message)
                elif what_config[1] == configword:
                    if 0 <= 2 < len(text):
                        isString = isinstance(text[2], str)
                        if isString:
                            if text[2] == 'true':
                                t = (text[2],self.bot_id,self.group_id)
                                c.executemany("UPDATE config SET allownsfw=? WHERE (botid=? AND groupid=?)", (t))
                                t = [(self.bot_name),]
                                c.execute("SELECT allownsfw FROM config WHERE (name=?)", (t))
                                allownsfw = c.fetchone()
                                print("Just updated allownsfw, expected output is 'true', here it is- %s" % (allownsfw))
                                conn.commit()
                                conn.close()
                                message = "Updated status of allownsfw - "
                                message += text[2]
                                self.send_message(message)
                            elif text[2] == 'false':
                                t = (text[2],self.bot_id,self.group_id)
                                c.executemany("UPDATE config SET allownsfw=? WHERE (botid=? AND groupid=?)", (t))
                                t = [(self.bot_name),]
                                c.execute("SELECT allownsfw FROM config WHERE (name=?)", (t))
                                allownsfw = c.fetchone()
                                print("Just updated allownsfw, expected output is 'false', here it is- %s" % (allownsfw))
                                conn.commit()
                                conn.close()
                                message = "Updated status of allownsfw - "
                                message += text[2]
                                self.send_message(message)
                            else:
                                self.send_message("Incorrect usage, expected true|false\nUsage !config allownsfw <true|false>")
                    else:
                        message = "Current status of allownsfw - "
                        message += self.allow_nsfw
                        self.send_message(message)
                elif what_config[2] == configword:
                    if 0 <= 2 < len(text):
                        isString = isinstance(text[2], str)
                        if isString:
                            if text[2] == 'true':
                                t = (text[2],self.bot_id,self.group_id)
                                c.executemany("UPDATE config SET allowrepost=? WHERE (botid=? AND groupid=?)", (t))
                                t = [(self.bot_name),]
                                c.execute("SELECT allowrepost FROM config WHERE (name=?)", (t))
                                allowrepost = c.fetchone()
                                print("Just updated allowrepost, expected output is 'true', here it is- %s" % (allowrepost))
                                conn.commit()
                                conn.close()
                                message = "Updated status of allowrepost - "
                                message += text[2]
                                self.send_message(message)
                            elif text[2] == 'false':
                                t = (text[2],self.bot_id,self.group_id)
                                c.executemany("UPDATE config SET allowrepost=? WHERE (botid=? AND groupid=?)", (t))
                                t = [(self.bot_name),]
                                c.execute("SELECT allowrepost FROM config WHERE (name=?)", (t))
                                allowrepost = c.fetchone()
                                print("Just updated allowrepost, expected output is 'false', here it is- %s" % (allowrepost))
                                conn.commit()
                                conn.close()
                                message = "Updated status of allowrepost - "
                                message += text[2]
                                self.send_message(message)
                            else:
                                self.send_message("Incorrect usage, expected true|false\nUsage !config allowrepost <true|false>")
                    else:
                        message = "Current status of allowrepost - "
                        message += self.allow_reposts
                        self.send_message(message)
                else:
                    self.send_message("Sorry, I can't find that config! This is the config message I received-\n%s" % (text))
        else:
            self.send_message("Sorry, this is only for authenticated users.")

    def send_meme(self, mes, att, gid, text, sender_name):
        start = time.time()
        meme_message = "Meme response-\n'"
        rand = random.randint(0, self.real_len)
        subreddit = self.meme_source[rand]
        print(subreddit)
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


    def send_help(self, mes, att, gid, text, sender_name):
        help_message = "Empuorg Bot Commands-\n" + "Version 0.1b\n" + "!memes - searches for a random meme from your meme suppliers in the config\n" + "!info - prints information for the group\n" + "!config - edits group config\n" + "!help - displays help commands\n"

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