import sys
import os
import json
from threading import Thread

# import quizbot.QuizBotGroupMe as QuizBotGroupMe
import quizbot.QuizBotDiscord as QuizBot

if len(sys.argv) is 2: #config file is specified
    config_file = os.path.normpath(sys.argv[1])
else:
    config_file = os.path.join('.', 'data', 'config.json')

with open(config_file) as data_file:
    config = json.load(data_file)

# QuizBotGroupMe.init()

# QuizBotGroupMe.listen(port=config['listening_port'])

quizbot = QuizBot.QuizBotDiscord()

QuizBot.client.run(quizbot.init("NjQ0MTk2ODU3MTEwODU1Njkw.Xcwhzg.gDcKMzfGgnkUVck-UEjCWnqUr3E"))