# discord wrapper for quizbot

import discord, sqlite3, logging, re, os, time

# main functions
from modules.QuizBotHelp import QuizBotHelp
from modules.QuizBotFunSayings import QuizBotFunSayings
from modules.QuizBotQuizzer import QuizBotQuizzer
from modules.QuizBotSendRedditMeme import QuizBotSendRedditMeme

discordlogger = logging.getLogger(__name__)

# discordlogger.basicConfig(level=logging.DEBUG,filename='logs/discord.log', filemode='w', format='QuizBot[DISCORD]: %(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

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
    def __init__(self, botname):
        self.awaiting_response = False
        self._init_regexes()
        self.bot_name = botname
    
    def _init_regexes(self):
        self.likes = re.compile("(^!likes$)")
        self.likesrank = re.compile("(^!rank$)")
        self.randommeme = re.compile("(^!meme$)")
        self.groupinfo = re.compile("(^!info$)")
        self.stats = re.compile("(^!stats$)")
        self.help_regex = re.compile("(^!help)")
        self.config = re.compile("(^!config)")
        self.authenticate = re.compile("(^!authenticate)")
        self.quiz = re.compile("(^!quiz)")
        self.hacking_joke = re.compile("(^!hack)")
        self.fred_joke = re.compile("(^!fred)")
        self.optregex = re.compile("(^!opt)")
        self.text = re.compile("(^!test)")

        self._construct_regexes()

    def _construct_regexes(self):
        self.regex_actions = [
            ("Help", self.help_regex, self.send_help),
            ("Fred", self.fred_joke, self.fred_function),
            ("Meme", self.randommeme, self.send_meme),
            ("Quiz", self.quiz, self.quizzer)
        ]
        discordlogger.info("Initialized regex.")

    def get_gid(self, groupid):
        self.group_id = groupid

    def send_help(self, text, name):
        x = QuizBotHelp(text)
        return x.response

    def fred_function(self, text, name):
        x = QuizBotFunSayings(name)
        return x.response

    def send_meme(self, text, name):
        x = QuizBotSendRedditMeme(['dankchristianmemes'], 1)
        return x.response

    def quizzer(self, text, sender_name):
        print(self.awaiting_response)
        if self.awaiting_response == False:
            self.quizboi = QuizBotQuizzer(["colin_be_rockin"], sender_name, False)
            self.quizboi.start_quiz(text)
            time.sleep(1)
            self.awaiting_response = self.quizboi.awaiting_response
            return self.quizboi.response
        elif self.awaiting_response == True:
            time.sleep(1)
            self.awaiting_response = self.quizboi.awaiting_response
            self.quizboi.continue_quiz(text, sender_name)
            if self.quizboi.goodjob:
                response = self.quizboi.goodjob + "\n"
            if self.quizboi.finishedQuiz == False and self.quizboi.correct == True:
                response += self.quizboi.response
                return response
            elif self.quizboi.finishedQuiz == True:
                response += "\nFinished quiz! Generating results\n"
                response += self.quizboi.response
                return response
            elif self.quizboi.finishedQuiz != True and self.quizboi.finishedQuiz != False:
                discordlogger.info("Finished quiz is broken, error")

    def init(self, token):
        return token

client = discord.Client()
quizbot = QuizBotDiscord(client.user)

@client.event
async def on_ready():
    discordlogger.info("Logged in and ready for commands. User - {0.user}".format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    print(message.author)
    print(quizbot.awaiting_response)
    if message.author.nick == None:
        sender = str(message.author)
    else:
        sender = message.author.nick
    text = message.content.strip()
    if quizbot.awaiting_response == False:
        for type, regex, action in quizbot.regex_actions:
            mes = regex.match(text)
            if mes:
                discordlogger.info(f'Received message with type:{type} and message:{text}')
                # quizbot.get_gid(discord.Guild)
                print(discord.Guild)
                await message.channel.send(action(text, sender))
    else:
        print("I am waiting for a message")
        await message.channel.send(quizbot.quizzer(text, sender))

if __name__ == "__main__":
    client.run(quizbot.init(""))