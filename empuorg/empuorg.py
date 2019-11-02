# fair warning to y'all. this is gonna be wack
# it is very wack
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
        logging.info(f"Reddit read only is - {reddit.read_only}")
        self.groupme_url = "https://api.groupme.com/v3/bots/post"

        # quizzing variables
        self.awaiting_response = False
        self.current_quiz = []
        self.current_question = 0
        self.quizbonuses = False
        self.useReddit = True
        self.keeping_score = []
        self.playerindex = 0
        self.quiztime = 0
        
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
            ("Quiz", self.quiz, self.start_quizzer),
            ("Joke/EasterEgg", self.hacking_joke, self.hack_joke)
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
        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        t = (self.bot_id, self.group_id)
        memesource = []
        for row in c.execute("SELECT subreddit FROM memesource WHERE (botid=? AND groupid=?)", (t)):
            memesource.append(row[0])
        logging.info(f"Inside _getmemesource: memesource should be populated here it is- {memesource}")
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
                            logging.info("%s and id#%s did not match group id#%s" %(name, id, gid))
                        else:
                            logging.info("%s and id#%s matched group id#%s" % (name, id, gid))
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
                mes = "none"
                att = attachments
                gid = groupid
                self.continue_quiz(mes, att, gid, message, sender_name)
            else:
                self.send_message("Error - awaiting_response is broken, setting it to False in order to avoid an infinite loop", 1)
                self.awaiting_response = False
    
    def send_likes(self, mes, att, gid, text, sender_name):
        self.send_message("Unfortunately, %s this is not currently working. Stay tuned!" % (sender_name), 1)

    def send_info(self, mes, att, gid, text, sender_name):
        self.send_message("Unfortunately, %s this is not currently working. Stay tuned!" % (sender_name), 1)

    def send_rank(self, mes, att, gid, text, sender_name):
        self.send_message("Unfortunately, %s this is not currently working. Stay tuned!" % (sender_name), 1)

    def start_quizzer(self, mes, att, gid, text, sender_name):
        self.quizstop = time.time()
        self.playerindex = 0
        sender_name = sender_name.lower()
        sender_name = sender_name.replace(" ", "_")
        if sender_name in self.authenticatedUsers:
            self.current_quiz = []
            counter = 0
            questioncount = text.replace("!quiz ", "")
            if int(questioncount) > 25:
                self.send_message("25 is the max amount of questions I can quiz over at this time.", 1)
            while counter < int(questioncount) and int(questioncount) <= 25:
                sections = self.quizmaterial['acts']['sections']
                sections = list(sections.keys())
                quiz_indexer = len(sections) - 1
                rand = random.randint(0,quiz_indexer)
                quiz_section = sections[rand]
                verse = self.quizmaterial['acts']['sections'][quiz_section]
                verse = list(verse.keys())
                quiz_indexer = len(verse) - 1
                rand = random.randint(0,quiz_indexer)
                quiz_verse = verse[rand]
                questions = self.quizmaterial['acts']['sections'][quiz_section][quiz_verse]
                questions = list(questions.keys())
                quiz_indexer = len(questions) - 1
                rand = random.randint(0,quiz_indexer)
                if self.quizbonuses == False:
                    quiz_question = questions[rand]
                    questions = self.quizmaterial['acts']['sections'][quiz_section][quiz_verse]
                    quiz_questionanswer = questions.get(quiz_question)
                    quizid = counter + 1
                    quiz = [quizid, quiz_section, quiz_verse, quiz_question, quiz_questionanswer]
                    if quiz in self.current_quiz:
                        logging.info("This question was already selected.")
                    elif quiz not in self.current_quiz:
                        self.current_quiz.append(quiz)
                        counter += 1
                    else:
                        logging.info("Failure to select a question, adding 1 to counter to avoid infinite loop")
                        counter += 1
                elif self.quizbonuses == True:
                    pass
                else:
                    pass
                if quiz_indexer != len(sections) - 1:
                    pass
            logging.info(self.current_quiz)
            message = "{}) Here is your question from the section '{}': {} ({})".format(self.current_quiz[0][0], self.current_quiz[0][1], self.current_quiz[0][3], self.current_quiz[0][2])
            self.awaiting_response = True
            self.current_question = 0
            self.send_message(message, 1)
        else:
            self.send_message("Sorry, this is only for authenticated users :/", 1)

    def continue_quiz(self, mes, att, gid, text, sender_name):
        response = text.lower()
        response = response.rstrip()
        logging.info(response)
        cq = self.current_question
        index = cq
        logging.info(cq)
        logging.info(index)
        logging.info(self.current_question)
        logging.info(self.current_quiz[index][4])
        if isinstance(self.current_quiz[index][4], list):
            if "," in response:
                response = response.split(', ')
            elif "and" in response:
                response = response.split(' and ')
            self.current_quiz[index][4] = sorted(self.current_quiz[index][4])
            response = sorted(response)
        if isinstance(self.current_quiz[index][4], str):
            if response in self.current_quiz[index][4]:
                name = sender_name.split(' ')
                name = name[0]
                message = "Good job {} you got that one right!".format(name)
                score = 1
                player = [name, score]
                while self.playerindex <= len(self.keeping_score):
                    if self.playerindex == len(self.keeping_score):
                        self.keeping_score.append(player)
                        logging.info(self.keeping_score)
                        self.playerindex += 1
                        break
                    elif name in self.keeping_score[self.playerindex]:
                        self.keeping_score[self.playerindex][1] += 1
                        logging.info(self.keeping_score)
                        self.playerindex += 1
                        break
                    else:
                        logging.info("Player not found, iterating again")
                        self.playerindex += 1
                self.playerindex = 0
                self.send_message(message, 1)
                self.current_question += 1
                index += 1
                if self.current_question < len(self.current_quiz):
                    message = "{}) Here is your question from the section '{}': {} ({})".format(self.current_quiz[index][0], self.current_quiz[index][1], self.current_quiz[index][3], self.current_quiz[index][2])
                    self.send_message(message, 5)
                else:
                    self.send_message("Finished quiz! Resuming normal commands.", 1)
                    self.quiztime = time.time() - self.quizstop
                    self.quiztime = time.strftime("%M:%Ss", time.gmtime(self.quiztime))
                    message = "Time taken: {}\nScore Results-\n".format(self.quiztime)
                    self.quiztime = 0
                    self.keeping_score = sorted(self.keeping_score, key = lambda x: int(x[1]), reverse=True)
                    for player in self.keeping_score:
                        message += "{}: {}\n".format(player[0],[player[1]])
                    self.send_message(message, 1)
                    self.awaiting_response = False
            else:
                logging.info("Got incorrect answer %s" % (text))
        elif isinstance(self.current_quiz[index][4], list):
            correctanswers = 0
            indexer = 0
            for a in response:
                if a in self.current_quiz[index][4][indexer]:
                    indexer += 1
                    correctanswers += 1
                else:
                    logging.info("%a is not correct" % (a))
            logging.info(correctanswers)
            logging.info("The number of correct answers is above me")
            logging.info(len(self.current_quiz[index][4]))
            logging.info("The number of answers is above me")
            if correctanswers == len(self.current_quiz[index][4]):
                name = sender_name.split(' ')
                name = name[0]
                message = "Good job {} you got that one right!".format(name)
                score = 1
                player = [name, score]
                while self.playerindex <= len(self.keeping_score):
                    if self.playerindex == len(self.keeping_score):
                        self.keeping_score.append(player)
                        logging.info(self.keeping_score)
                        self.playerindex += 1
                        break
                    elif name in self.keeping_score[self.playerindex]:
                        self.keeping_score[self.playerindex][1] += 1
                        logging.info(self.keeping_score)
                        self.playerindex += 1
                        break
                    else:
                        logging.info("Player not found, iterating again")
                        self.playerindex += 1
                self.playerindex = 0
                self.send_message(message, 1)
                self.current_question += 1
                index += 1
                if self.current_question < len(self.current_quiz):
                    message = "{}) Here is your question from the section '{}': {} ({})".format(self.current_quiz[index][0], self.current_quiz[index][1], self.current_quiz[index][3], self.current_quiz[index][2])
                    self.send_message(message, 5)
                else:
                    self.send_message("Finished quiz! Resuming normal commands.", 1)
                    self.quiztime = time.time() - self.quizstop
                    self.quiztime = time.strftime("%M:%Ss", time.gmtime(self.quiztime))
                    message = "Time taken: {}\nScore Results-\n".format(self.quiztime)
                    self.quiztime = 0
                    self.keeping_score = sorted(self.keeping_score, key = lambda x: int(x[1]), reverse=True)
                    for player in self.keeping_score:
                        message += "{}: {}\n".format(player[0],[player[1]])
                    self.send_message(message, 1)
                    self.awaiting_response = False
            else:
                logging.info("Got incorrect answer %s" % (text))
        else:
            logging.info("Failed to determine type of answer. (Expected str or list)")

    def update_config(self, mes, att, gid, text, sender_name):
        sender_name = sender_name.lower()
        sender_name = sender_name.replace(" ", "_")
        if sender_name in self.authenticatedUsers:
            conn = sqlite3.connect('config.db')
            c = conn.cursor()
            text = text.lower()
            what_config = ['subreddit','allownsfw','allowrepost']
            text = text.split(' ')
            logging.info(text)
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
                                logging.info("Just updated memesource here it is- %s" % (memesource))    
                                conn.commit()
                                conn.close()
                                message = "Updated subreddit list, added - "
                                message += text[3]
                                self.send_message(message, 1)
                            else:
                                self.send_message("You didn't include a subreddit!\nUsage - !config subreddit add <subreddit>", 1)
                        elif text[2] == 'delete':
                            if 0 <= 3 < len(text):
                                isString = isinstance(text[3], str)
                                t = [(text[3],self.bot_name)]
                                c.executemany("DELETE FROM memesource WHERE (subreddit=? AND name=?)", (t))
                                memesource = []
                                t = [(self.bot_name),]
                                for row in c.execute("SELECT subreddit FROM memesource WHERE (name=?)", (t)):
                                    memesource.append(row[0])
                                logging.info("Just updated memesource here it is- %s" % (memesource))    
                                conn.commit()
                                conn.close()
                                message = "Updated subreddit list, removed - "
                                message += text[3]
                                self.send_message(message, 1)
                            else:
                                self.send_message("You didn't include a subreddit!\nUsage - !config subreddit add <subreddit>", 1)
                        else:
                            self.send_message("Incorrect usage, expected add|delete\nUsage - !config subreddit <add|delete>", 1)
                    else:
                        message = "Current enabled subreddits to pull from -"
                        for subreddit in self.meme_source:
                            message += "\n{}".format(subreddit)
                        self.send_message(message, 1)
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
                                logging.info("Just updated allownsfw, expected output is 'true', here it is- %s" % (allownsfw))
                                conn.commit()
                                conn.close()
                                message = "Updated status of allownsfw - "
                                message += text[2]
                                self.send_message(message, 1)
                            elif text[2] == 'false':
                                t = (text[2],self.bot_id,self.group_id)
                                c.executemany("UPDATE config SET allownsfw=? WHERE (botid=? AND groupid=?)", (t))
                                t = [(self.bot_name),]
                                c.execute("SELECT allownsfw FROM config WHERE (name=?)", (t))
                                allownsfw = c.fetchone()
                                logging.info("Just updated allownsfw, expected output is 'false', here it is- %s" % (allownsfw))
                                conn.commit()
                                conn.close()
                                message = "Updated status of allownsfw - "
                                message += text[2]
                                self.send_message(message, 1)
                            else:
                                self.send_message("Incorrect usage, expected true|false\nUsage !config allownsfw <true|false>", 1)
                    else:
                        message = "Current status of allownsfw - "
                        message += self.allow_nsfw
                        self.send_message(message, 1)
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
                                logging.info("Just updated allowrepost, expected output is 'true', here it is- %s" % (allowrepost))
                                conn.commit()
                                conn.close()
                                message = "Updated status of allowrepost - "
                                message += text[2]
                                self.send_message(message, 1)
                            elif text[2] == 'false':
                                t = (text[2],self.bot_id,self.group_id)
                                c.executemany("UPDATE config SET allowrepost=? WHERE (botid=? AND groupid=?)", (t))
                                t = [(self.bot_name),]
                                c.execute("SELECT allowrepost FROM config WHERE (name=?)", (t))
                                allowrepost = c.fetchone()
                                logging.info("Just updated allowrepost, expected output is 'false', here it is- %s" % (allowrepost))
                                conn.commit()
                                conn.close()
                                message = "Updated status of allowrepost - "
                                message += text[2]
                                self.send_message(message, 1)
                            else:
                                self.send_message("Incorrect usage, expected true|false\nUsage !config allowrepost <true|false>", 1)
                    else:
                        message = "Current status of allowrepost - "
                        message += self.allow_reposts
                        self.send_message(message, 1)
                else:
                    self.send_message("Sorry, I can't find that config! This is the config message I received-\n%s" % (text), 1)
        else:
            self.send_message("Sorry, this is only for authenticated users.", 1)

    def send_meme(self, mes, att, gid, text, sender_name):
        start = time.time()
        if self.useReddit == True:
            meme_message = "Meme response-\n'"
            rand = random.randint(0, self.real_len)
            subreddit = self.meme_source[rand]
            logging.info(subreddit)
            submission_list = []
            for submission in reddit.subreddit(subreddit).hot(limit=10):
                if submission.stickied != True:
                    submission_list.append(submission)
                else:
                    logging.info("We don't approve of stickied messages")
            submission_list_length = len(submission_list) - 1
            rand = random.randint(0,submission_list_length)
            logging.info("Got a random submission index of %d out of %d\nIt has an upvote ratio of %d" % (rand, submission_list_length, submission_list[rand].upvote_ratio))
            logging.info("Printing url link for post '%s'-\n" % (submission_list[rand].title))
            if submission_list[rand].selftext == "":
                logging.info(submission_list[rand].url)
                result = submission_list[rand].url
            else:
                logging.info(submission_list[rand].shortlink)
                result = submission_list[rand].shortlink
            meme_message += submission_list[rand].title
            meme_message += "' from the subreddit '"
            meme_message += submission_list[rand].subreddit.display_name
            meme_message += "'\n"
            meme_message += result
            meme_message += "\nI hope you enjoy!\n"
            meme_message += "response_time: "
        elif self.useReddit == False:
            pass
        response_time = time.time() - start
        if time.strftime("%S", time.gmtime(response_time)) == "00":
            meme_message += "< 0s"
        else:
            meme_message += time.strftime("%Ss", time.gmtime(response_time))

        self.send_message(meme_message, 1)


    def send_help(self, mes, att, gid, text, sender_name):
        help_message = "Empuorg Bot Commands-\n" + "Version 0.2b\n" + "!memes - searches for a random meme from your meme suppliers in the config\n" + "!info - prints information for the group\n" + "!config - edits group config\n" + "!help - displays help commands\n"

        self.send_message(help_message, 1)

    def hack_joke(self, mes, att, type, text, sender_name):
        message = "Begining hacking sequence...\nSetting variables....\nsender_name: {}\ngroup_id:{}\ndate{}\nattempting remote login....\nsuccess".format(sender_name, self.group_id, time.strftime("%j/%m/%Y", time.gmtime(time.time())))
        self.send_message(message, 1)
    
    def send_message(self, message, t):
        data = {"bot_id": self.bot_id, "text": str(message)}
        time.sleep(t)
        requests.post(self.groupme_url, json=data)
        logging.info(f"Just sent a message-\n{message}\n")


# init bot
def init(bot_id=0):
    global bot
    bot = Empuorg(bot_id=bot_id)
    return bot


# listen and send all messages to the message router
def listen(server_class=HTTPServer, handler_class=MessageRouter, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()