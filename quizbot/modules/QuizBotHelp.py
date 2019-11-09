# class for help message

class QuizBotHelp:
    def __init__(self):
        message = "QuizBot Bot Commands-\nVersion 0.3b\n"
        message += "!meme - searches for a random meme from your meme suppliers in the config\n"
        message += "!info - prints information about the group\n"
        message += "!config - edits group config\n"
        message += "!fred - get a message from Fred\n"
        message += "!help - displays help commands\n"
        self.response = message