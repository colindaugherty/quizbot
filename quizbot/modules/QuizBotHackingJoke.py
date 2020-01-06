# a joke to make the Bible Bowl kids think they 'hacked' quizbot

import time, random

class QuizBotHackingJoke:
    def __init__(self, groupid, text, sender_name):
        text = text.split()
        passwords = ["biblebowlrulz", "password123", "1023914023190", "Thi5_15_4_v3ry_s3cure_p455w0RD", "quizbot", "myDog"]
        emails = ["da_bestBowler_to_ever_Bible@yahoo.com", "soontobenationalchampion@gmail.com", "supercooldude123@rocketmail.com", "this_is_my_5th_email@gmail.com"]
        randpassword = passwords[random.randint(0, len(passwords) - 1)]
        randemail = emails[random.randint(0, len(emails) - 1)]
        if len(text) > 1:
            message = f"Begining to hack {text[1]}\nCracking password...\npassword found\nsending password: {randpassword}\nfound email: {randemail}\nYou now have access to {text[1]}'s account. Be wise."
        else:
            message = "Begining hacking sequence...\nSetting variables....\n\nsender_name: {}\ngroup_id: {}\ndate: {}\n\nattempting remote login....\nsuccess\n\n{} you are now totally in the system. Good job. Proud of you.".format(sender_name, groupid, time.strftime("%j/%m/%Y", time.gmtime(time.time())), sender_name)

        self.response = message