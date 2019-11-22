# discord wrapper for quizbot

import discord, sqlite3, logging, re, os, time

# main functions
from .modules.QuizBotHelp import QuizBotHelp
from .modules.QuizBotFunSayings import QuizBotFunSayings
from .modules.QuizBotQuizzer import QuizBotQuizzer

logging.basicConfig(level=logging.DEBUG,filename='access.log', filemode='w', format='QuizBot[DISCORD]: %(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

conn = sqlite3.connect('config.db')

logging.info("Started program. Hello world!")

config_file = os.path.join('.', 'data', 'config.json')
quiz_file = os.path.join('.', 'data', 'quiz_material.json')

class QuizBotDiscord():
    def __init__(self):
        self.awaiting_response = False
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
            ("Quiz", self.quiz, self.quizzer),
            ("Testing", self.text, self.testing_quizzer)
        ]
        logging.info("Initialized regex.")

    def send_help(self, text, name):
        x = QuizBotHelp(text)
        return x.response

    def fred_function(self, text, name):
        x = QuizBotFunSayings(name)
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
                logging.info("Finished quiz is broken, error")

    def testing_quizzer(self, text, name):
        self.quizzerbotboi = QuizBotQuizzer(["colin be rockin"], name, False)
        self.quizzerbotboi.start_quiz(text)
        print(self.quizzerbotboi.awaiting_response)
        return self.quizzerbotboi.response

    def init(self, token):
        return token

quizbot = QuizBotDiscord()

client = discord.Client()

@client.event
async def on_ready():
    logging.info("Logged in and ready for commands. User - {0.user}".format(client))

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
                logging.info(f'Received message with type:{type} and message:{text}')
                await message.channel.send(action(text, sender))
    else:
        print("I am waiting for a message")
        await message.channel.send(quizbot.quizzer(text, sender))

if __name__ == "__main__":
    client.run(quizbot.init("NjQ0MTk2ODU3MTEwODU1Njkw.Xcwhzg.gDcKMzfGgnkUVck-UEjCWnqUr3E"))