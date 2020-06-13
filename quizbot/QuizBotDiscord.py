# discord wrapper for quizbot

import discord, sqlite3, logging, re, os, time, discord.utils

from .QuizBotDataHandler import QuizBotDataHandler

# message functions
from .modules.QuizBotHelp import QuizBotHelp
from .modules.QuizBotFunSayings import QuizBotFunSayings
from .modules.QuizBotHackingJoke import QuizBotHackingJoke
from .modules.QuizBotQuizzer import QuizBotQuizzer
from .modules.QuizBotSendRedditMeme import QuizBotSendRedditMeme
from .modules.QuizBotAnnounceWinners import QuizBotAnnounceWinners

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
        if self.meme_source == None:
            self.real_len = 0    
        else:
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
        x = QuizBotHackingJoke(self.group_id, text, name)
        return x.response

    def send_meme(self, text, name):
        x = QuizBotSendRedditMeme(self.meme_source, self.real_len)
        return x.response

    def opt(self, text, sender_name):
        x = QuizBotOptIO(sender_name, text, self.group_id, self.bot_name, datahandler)
        return x.response

    def quizzer(self, text, sender_name, mode):
        if mode == 'start':
            self.quizboi = QuizBotQuizzer(self.authenticated_users, sender_name, False, datahandler, self.bot_name, self.group_id)
            return self.quizboi.start_quiz(text)
        elif mode == 'continue':
            return self.quizboi.continue_quiz(text, sender_name)

    def announceWinners(self):
        x = QuizBotAnnounceWinners(self.bot_name, self.group_id, datahandler)
        return x.response

    def init(self, token):
        return token

client = discord.Client()
quizbot = QuizBotDiscord()

@client.event
async def on_ready():
    discordlogger.info("Logged in and ready for commands. User - {0.user}".format(client))

@client.event
async def on_message(message):
    channel = str(message.channel)
    discordlogger.info(f"\n\nmessage sent in channel {channel}\n\n")

    # id message origin
    if message.guild in client.guilds:
        groupid = message.guild
        groupid = groupid.id
    uid = message.author.id
    
    # get name of sender
    sender = client.get_user(uid)
    sender = sender.display_name
    if message.author.nick != None:
        sender = message.author.nick

    # get message text ready for processing
    text = message.content
    text = text.strip()

    # process message and send response
    if "quiz-room" or "quizbot" or "study-room" in channel:
        discordlogger.info(f"\n\nin quiz room\n\n")
        quizbot._set_variables(client.user.name, groupid)
        text = message.content
        if message.author == client.user:
            if "Score Results" in text:
                time.sleep(5)
                await message.channel.send(quizbot.quizzer("!quiz 15", "colin", "start"))
        elif "!quiz 15" in text and sender == "colin":
            await message.channel.send(quizbot.quizzer("!quiz 15", "colin", "start"))
        else:
            await message.channel.send(quizbot.quizzer(text, sender, "continue"))
    elif channel == "welcome":
        if message.author == client.user:
            return
        text = message.content
        if "!team" in text:
            text = text.replace("!team", "")
            text = text.strip
            if ", " in text:
                text = text.replace(", ", " ")
            role_list = text.split()
            for role in role_list:
                role = discord.utils.get(message.server.roles, name=role)
                try:
                    await message.author.add_roles(message.author, role)
                    await message.channel.send(f"Added role {role.name} to you.")
                except discord.Forbidden:
                    await message.channel.send("I can't add roles :/")
    elif "general" in channel:
        discordlogger.info(f"\n\nin a general chat\n\n")
        if message.author == client.user:
            return
        if "!quiz" in text:
                await message.channel.send("Sorry! That command isn't allowed in here, use #study-room for quizzing functions!")
        for type, regex, action, in quizbot.regex_actions:
            mes = regex.match(text)
            if mes:
                discordlogger.info(f'Received message with type:{type} and message:{text}')
                quizbot._set_variables(client.user.name, groupid)
                await message.channel.send(action(text, sender))
    elif channel == "moderation-log":
        quizbot._set_variables(client.user.name, groupid)
        if text == "!announce-winners":
            if message.guild in client.guilds:
                guild = message.guild
            channel = discord.utils.get(guild.channels, name="announcements", type=discord.ChannelType.text)
            await channel.send(quizbot.announceWinners())
    else:
        discordlogger.info(f'Wrong channel! Channel I got was {channel}')

if __name__ == "__main__":
    client.run(quizbot.init(""))