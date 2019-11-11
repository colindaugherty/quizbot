# class for help message

class QuizBotHelp:
    def __init__(self):
        message = "QuizBot Bot Commands-\nVersion 0.4b\n"
        message += "!meme - searches for a random meme from your meme suppliers in the config\n"
        message += "!opt <in|out>- opt in and out of events run by the bot, include the event for more specific opting\n"
        message += "!config - edits group config\n"
        message += "!fred - get a message from Fred\n"
        message += "!help - displays help commands\n"
        self.response = message