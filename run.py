import sys
import os
import json, logging
from threading import Thread

import quizbot.QuizBotDiscord as QuizBot
import quizbot.QuizBotGroupMe as QuizBotGroupMe

print("Quizbot is starting up now. Hello World!")
logging.basicConfig(level=logging.DEBUG,filename='access.log', filemode='w', format='QuizBot: %(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.info("Hello World! This is the first real line of quizbot")

if len(sys.argv) is 2: #config file is specified
    config_file = os.path.normpath(sys.argv[1])
else:
    config_file = os.path.join('.', 'data', 'config.json')

with open(config_file) as data_file:
    config = json.load(data_file)

# QuizBotGroupMe.init()
# QuizBotGroupMe.listen(port=config['listening_port'])

quizbot = QuizBot.QuizBotDiscord()
QuizBot.client.run(quizbot.init(config['discord_key']))