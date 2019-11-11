# class for help message

import logging

class QuizBotHelp:
    def __init__(self, text):
        self.found_command = False
        text = text.lower()
        text = text.split()
        if len(text) == 2:
            command_help = [
                ["Help","!help <command>","Displays commands and their syntax/usage"],
                ["Opt","!opt <in|out> (optional:elimination|newsroom)","Will opt you in or out of specific quizbot events, such as newsroom and elimination"],
                ["Config","requires auth\n!config <configname>","Edits config per group, must be used by authenticated users"],
                ["Fred","!fred","A funny phrase generator, name idea by Vanessa"],
                ["Meme","!meme","Meme generator, will pull a random meme from your meme sources."]
            ]
            for command in command_help:
                if text[1] == command[0].lower():
                    self.response = "Usage: {}\n{}: {}".format(command[1], command[0], command[2])
                    self.found_command = True
            if self.found_command == True:
                logging.info("Found command {} successfully.".format(text[1]))
            elif self.found_command == False:
                self.response = "Unable to find that command, maybe you mistyped?"
                logging.info("Didn't find command {}".format(text[1]))
            else:
                logging.info(self.found_command)
        elif len(text) == 1:
            message = "QuizBot Bot Commands-\nVersion 0.4b\n"
            message += "!meme - searches for a random meme from your meme suppliers in the config\n"
            message += "!opt <in|out>- opt in and out of events run by the bot, include the event for more specific opting\n"
            message += "!config - edits group config\n"
            message += "!fred - get a message from Fred\n"
            message += "!help - displays help commands\n"
            self.response = message
        elif len(text) > 2:
            self.response = "You've asked for too many words, I can't help you..."
        else:
            logging.info("HelpModule: Text has confused me - {}".format(text))