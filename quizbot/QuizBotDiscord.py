# discord wrapper for quizbot

import discord, sqlite3, logging, re, os, time

from .QuizBotDataHandler import QuizBotDataHandler

# message functions
from .modules.QuizBotHelp import QuizBotHelp
from .modules.QuizBotFunSayings import QuizBotFunSayings
from .modules.QuizBotHackingJoke import QuizBotHackingJoke
from .modules.QuizBotQuizzer import QuizBotQuizzer
from .modules.QuizBotSendRedditMeme import QuizBotSendRedditMeme

# database functions
from .modules.QuizBotAuthenticateUser import QuizBotAuthenticateUser
from .modules.QuizBotUpdateConfig import QuizBotUpdateConfig
from .modules.QuizBotOptIO import QuizBotOptIO
from .modules.QuizBotSetMemeSource import QuizBotSetMemeSource

datahandler = QuizBotDataHandler(discord=True)

discordlogger = logging.getLogger(__name__)
discordlogger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('logs/discord.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('QuizBot[DISCORD]: %(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the file handler to the logger
discordlogger.addHandler(handler)

discordlogger.info("Started program. Hello world!")

config_file = os.path.join('.', 'data', 'config.json')
quiz_file = os.path.join('.', 'data', 'quiz_material.json')

class QuizBotDiscord():
    def __init__(self):
        self.awaiting_response = False
        self._init_regexes()
    
    def _init_regexes(self):
        self.groupinfo = re.compile("(^!info$)")
        self.stats = re.compile("(^!stats$)")

        #finished
        self.help_regex = re.compile("(^!help)")
        
        self.fred_joke = re.compile("(^!fred)")
        self.hacking_joke = re.compile("(^!hack)")
        self.randommeme = re.compile("(^!meme$)")
        self.quiz = re.compile("(^!quiz)")

        self.config = re.compile("(^!config)")
        self.authenticate = re.compile("(^!authenticate)")
        self.deauthenticate = re.compile("(^!deauthenticate)")
        self.optregex = re.compile("(^!opt)")

        self._construct_regexes()

    def _construct_regexes(self):
        self.regex_actions = [
            ("Help", self.help_regex, self.send_help),
            ("Joke/EasterEgg", self.hacking_joke, self.hack_joke),
            ("Fred", self.fred_joke, self.fred_function),
            ("Meme", self.randommeme, self.send_meme),
            ("Quiz", self.quiz, self.quizzer),
            ("Authenticate", self.authenticate, self._authenticateUser),
            ("Authenticate", self.deauthenticate, self._authenticateUser),
            ("Config", self.config, self.update_config),
            ("Opting In/Out", self.optregex, self.opt)
        ]
        discordlogger.info("Initialized regex.")

    def _set_variables(self, botname, groupid):
        self.bot_name = botname
        self.group_id = groupid
        self.authenticated_users = self._getauthenticatedusers()
        self.meme_source = self._getmemesource()
        self.real_len = len(self.meme_source) - 1
        self.allow_nsfw = self._getallownsfw()
        self.allow_reposts = self._getallowreposts()

    def _authenticateUser(self, text, sender_name):
        x = QuizBotAuthenticateUser(sender_name, text, self.bot_name, self.group_id, datahandler)
        return x.response

    def update_config(self, text, sender_name):
        x = QuizBotUpdateConfig(self.authenticated_users, text, self.bot_name, self.group_id, sender_name, datahandler)
        return x.response

    def _getmemesource(self):
        # x = QuizBotSetMemeSource(self.bot_id, self.group_id)
        data = {"name" : self.bot_name, "groupid" : self.group_id, "table" : "memesource", "data": [self.bot_name, self.group_id]}
        memesource = datahandler.do("select", data)
        return memesource

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

    def send_help(self, text, name):
        x = QuizBotHelp(text)
        return x.response

    def fred_function(self, text, name):
        x = QuizBotFunSayings(name)
        return x.response

    def hack_joke(self, text, name):
        x = QuizBotHackingJoke(self.group_id, name)
        return x.response

    def send_meme(self, text, name):
        x = QuizBotSendRedditMeme(self.meme_source, self.real_len)
        return x.response

    def opt(self, text, sender_name):
        x = QuizBotOptIO(sender_name, text, self.group_id, self.bot_name, datahandler)
        return x.response

    def quizzer(self, text, sender_name):
        print(self.awaiting_response)
        if self.awaiting_response == False:
            self.quizboi = QuizBotQuizzer(self.authenticated_users, sender_name, False)
            self.quizboi.start_quiz(text)
            time.sleep(1)
            self.awaiting_response = self.quizboi.awaiting_response
            return self.quizboi.response
        elif self.awaiting_response == True:
            time.sleep(3)
            self.awaiting_response = self.quizboi.awaiting_response
            self.quizboi.continue_quiz(text, sender_name)
            if self.quizboi.goodjob:
                response = self.quizboi.goodjob + "\n"
            if self.quizboi.finishedQuiz == False and self.quizboi.correct == True:
                response += self.quizboi.response
                return response
            elif self.quizboi.finishedQuiz == True:
                self.awaiting_response = False
                response += "\nFinished quiz! Generating results\n"
                response += self.quizboi.response
                return response
            elif self.quizboi.finishedQuiz != True and self.quizboi.finishedQuiz != False:
                discordlogger.info("Finished quiz is broken, error")

    def init(self, token):
        return token

client = discord.Client()
quizbot = QuizBotDiscord()

@client.event
async def on_ready():
    discordlogger.info("Logged in and ready for commands. User - {0.user}".format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    print(message.author)
    print(quizbot.awaiting_response)
    if message.guild in client.guilds:
        groupid = message.guild
        groupid = groupid.id
    else:
        logging.info(f"If you're seeing this, I don't even know how this error happened. {message.guild}")
    uid = message.author.id
    # get name of the sender without identifier (identifier is not as relavant in smaller groups)
    sender = client.get_user(uid)
    sender = sender.display_name
    # if they have a nickname, use that instead
    if message.author.nick != None:
        sender = message.author.nick
    text = message.content
    text = text.strip()
    print(text)
    if quizbot.awaiting_response == False:
        for type, regex, action in quizbot.regex_actions:
            mes = regex.match(text)
            if mes:
                discordlogger.info(f'Received message with type:{type} and message:{text}')
                quizbot._set_variables(client.user.name, groupid)
                await message.channel.send(action(text, sender))
    else:
        print("I am waiting for a message")
        await message.channel.send(quizbot.quizzer(text, sender))

if __name__ == "__main__":
    client.run(quizbot.init(""))