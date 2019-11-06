# a joke to make the Bible Bowl kids think they 'hacked' quizbot

import time

class QuizBotHackingJoke:
    def __init__(self, groupid, sender_name):
        message = "Begining hacking sequence...\nSetting variables....\n\nsender_name: {}\ngroup_id: {}\ndate: {}\n\nattempting remote login....\nsuccess\n\n{} you are now totally in the system. Good job. Proud of you.".format(sender_name, groupid, time.strftime("%j/%m/%Y", time.gmtime(time.time())), sender_name)

        self.response = message