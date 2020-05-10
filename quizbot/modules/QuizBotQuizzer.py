# rewrite of the quizzing function, put into module form
# can probably be done better, but it's working for now

from difflib import SequenceMatcher
import time, random, os, logging, json

quiz_file = os.path.join('.', 'data', 'quiz_material.json')

class QuizBotQuizzer():
    def __init__(self, authenticated_users, sender_name, quizbonuses, handler, botname, groupid):
        self.authenticated_users = ["colin", "colin_d.", "mrcdaug"]
        self.sender_name = sender_name
        self.quizbonuses = quizbonuses
        self.current_quiz = []
        self.current_question = 0
        self.keeping_score = []
        self.playerindex = 0
        self.quiztime = 0
        self.finishedQuiz = False
        self.awaiting_response = False
        self.botname = botname
        self.groupid = groupid
        self.handler = handler

        with open(quiz_file) as data_file:
            self.quizmaterial = json.load(data_file)

        self.rules = self.quizmaterial["rules"]
        self.quizmaterial = self.quizmaterial["material"]

    def similar(self, answer, correct):
        logging.info("Comparing strings {} and {}".format(answer, correct))
        ratio = SequenceMatcher(None, answer, correct).ratio()
        ans_as_list = list(answer)
        cor_as_list = list(correct)
        
        letterratio = len(ans_as_list) / len(cor_as_list)
        logging.info("letterratio - {}".format(letterratio))
        if ratio > 0.65 and letterratio > 0.80:
            result = True
        else:
            result = False
        
        logging.info("Results of comparison-\n{} has a spellcheck ratio of {} and the length ratio between {} and {} is {}".format(answer, letterratio, answer, correct, ratio))
        return result

    def rulechecker(self, playeranswer, correctanswer):
        interchangeables = self.rules["interchangeable"]
        inter_list = list(interchangeables.keys())
        for key in inter_list:
            values = interchangeables.get(key)
            if playeranswer in values and correctanswer in values:
                return True
            elif playeranswer not in values and correctanswer in values:
                return False
            else:
                logging.info("Player answer not found in this rule set, retrying.")

    def start_quiz(self, text):
        self.quizstop = time.time()
        self.playerindex = 0
        sender_name = self.sender_name.lower()
        sender_name = sender_name.replace(" ", "_")
        if sender_name in self.authenticated_users:
            self.current_quiz = []
            counter = 0
            questioncount = text.replace("!quiz ", "")
            if int(questioncount) > 25:
                return "25 is the max amount of questions I can quiz over at this time."
            while counter < int(questioncount) and int(questioncount) <= 25:
                topics = self.quizmaterial
                topics = list(topics.keys())
                quiz_indexer = len(topics) - 1
                rand = random.randint(0,quiz_indexer)
                quiz_topic = topics[rand]
                sections = self.quizmaterial[quiz_topic]['sections']
                sections = list(sections.keys())
                quiz_indexer = len(sections) - 1
                rand = random.randint(0,quiz_indexer)
                quiz_section = sections[rand]
                verse = self.quizmaterial[quiz_topic]['sections'][quiz_section]
                verse = list(verse.keys())
                quiz_indexer = len(verse) - 1
                rand = random.randint(0,quiz_indexer)
                quiz_verse = verse[rand]
                questions = self.quizmaterial[quiz_topic]['sections'][quiz_section][quiz_verse]
                questions = list(questions.keys())
                quiz_indexer = len(questions) - 1
                rand = random.randint(0,quiz_indexer)
                if self.quizbonuses == False:
                    quiz_question = questions[rand]
                    questions = self.quizmaterial[quiz_topic]['sections'][quiz_section][quiz_verse]
                    quiz_questionanswer = questions.get(quiz_question)
                    quizid = counter + 1
                    quiz = [quizid, quiz_section, quiz_verse, quiz_question, quiz_questionanswer, quiz_topic]
                    if quiz in self.current_quiz:
                        logging.info("This question was already selected.")
                    elif quiz not in self.current_quiz:
                        self.current_quiz.append(quiz)
                        counter += 1
                    else:
                        logging.info("Failure to select a question, adding 1 to counter to avoid infinite loop")
                        counter += 1
                elif self.quizbonuses == True:
                    pass
                else:
                    pass
                if quiz_indexer != len(sections) - 1:
                    pass
            logging.info(self.current_quiz)
            if self.current_quiz != []:
                message = "{}) Here is your question from the section '{}': {} ({}-{})".format(self.current_quiz[0][0], self.current_quiz[0][1], self.current_quiz[0][3], self.current_quiz[0][5], self.current_quiz[0][2])
                self.awaiting_response = True
                self.current_question = 0
                return message
        else:
            return "Sorry, this is only for authenticated users :/"

    def continue_quiz(self, answer, sender_name):
        self.goodjob = False
        self.correct = False
        playeranswer = answer.lower()
        playeranswer = playeranswer.strip()
        if "'" in playeranswer:
            playeranswer = playeranswer.replace("'", "’")
        if " and " in playeranswer:
            playeranswer = playeranswer.replace(" and ", ", ")
        logging.info(playeranswer)
        cq = self.current_question
        index = cq
        logging.info(cq)
        logging.info(self.current_question)
        logging.info(self.current_quiz[index][4])
        if isinstance(self.current_quiz[index][4], list):
            if "," in playeranswer:
                playeranswer = playeranswer.split(', ')
            self.current_quiz[index][4] = sorted(self.current_quiz[index][4])
            playeranswer = sorted(playeranswer)
        if isinstance(self.current_quiz[index][4], str):
            if self.similar(playeranswer, self.current_quiz[index][4]) or self.rulechecker(playeranswer, self.current_quiz[index][4]):
                name = sender_name.split(' ')
                name = name[0]
                message = "Good job {} you got that one right!".format(name)

                data = {"name" : self.botname, "groupid" : self.groupid, "table" : "players", "data" : [self.botname, self.groupid, name]}
                checkForPlayer = self.handler.do("select", data)
                if checkForPlayer == None:
                    data = {"name" : self.botname, "groupid" : self.groupid, "table" : "players", "data" : [self.botname, self.groupid, name, 0, 1, 0, 1, 0]}
                    insertData = self.handler.do("insert", data)
                    if insertData == True:
                        message += "\nThis was your first correct answer this week! Yay!\n"
                else:
                    data = {"name" : self.botname, "groupid" : self.groupid, "table" : ["players", "questions"], "data" : [self.botname, self.groupid, name]}
                    updateData = self.handler.do("update", data)
                    if updateData == True:
                        message += "\nAdded that question to your tally board. Good job!\n"

                score = 1
                player = [name, score]
                while self.playerindex <= len(self.keeping_score):
                    if self.playerindex == len(self.keeping_score):
                        self.keeping_score.append(player)
                        logging.info(self.keeping_score)
                        self.playerindex += 1
                        break
                    elif name in self.keeping_score[self.playerindex]:
                        self.keeping_score[self.playerindex][1] += 1
                        logging.info(self.keeping_score)
                        self.playerindex += 1
                        break
                    else:
                        logging.info("Player not found, iterating again")
                        self.playerindex += 1
                self.playerindex = 0
                self.correct = True
                self.current_question += 1
                index += 1
                if self.current_question < len(self.current_quiz):
                    message += "{}) Here is your question from the section '{}': {} ({}-{})".format(self.current_quiz[index][0], self.current_quiz[index][1], self.current_quiz[index][3], self.current_quiz[index][5], self.current_quiz[index][2])
                    return message
                else:
                    self.awaiting_response = False
                    self.finishedQuiz = True
                    self.quiztime = time.time() - self.quizstop
                    self.quiztime = time.strftime("%M:%Ss", time.gmtime(self.quiztime))
                    message += "Finished quiz! Generating results\nTime taken: {}\nScore Results-\n".format(self.quiztime)
                    self.quiztime = 0
                    self.keeping_score = sorted(self.keeping_score, key = lambda x: int(x[1]), reverse=True)
                    for player in self.keeping_score:
                        message += "{}: {}\n".format(player[0],[player[1]])
                    return message
            else:
                logging.info("Got incorrect answer %s" % (answer))
        elif isinstance(self.current_quiz[index][4], list):
            correctanswers = 0
            indexer = 0
            for a in playeranswer:
                if self.similar(a, self.current_quiz[index][4][indexer]) or self.rulechecker(a, self.current_quiz[index][4]):
                    indexer += 1
                    correctanswers += 1
                else:
                    logging.info("%s is not correct" % (a))
            logging.info(correctanswers)
            logging.info("The number of correct answers is above me")
            logging.info(len(self.current_quiz[index][4]))
            logging.info("The number of answers is above me")
            if correctanswers == len(self.current_quiz[index][4]):
                name = sender_name.split(' ')
                name = name[0]
                message = "Good job {} you got that one right!".format(name)

                data = {"name" : self.botname, "groupid" : self.groupid, "table" : "players", "data" : [self.botname, self.groupid, name]}
                checkForPlayer = self.handler.do("select", data)
                if checkForPlayer == None:
                    data = {"name" : self.botname, "groupid" : self.groupid, "table" : "players", "data" : [self.botname, self.groupid, name, 0, 1, 0, 1, 0]}
                    insertData = self.handler.do("insert", data)
                    if insertData == True:
                        message += "\nThis was your first correct answer this week! Yay!"
                else:
                    data = {"name" : self.botname, "groupid" : self.groupid, "table" : ["players", "questions"], "data" : [self.botname, self.groupid, name]}
                    updateData = self.handler.do("update", data)
                    if updateData == True:
                        message += "\nAdded that question to your tally board. Good job!"

                score = 1
                player = [name, score]
                while self.playerindex <= len(self.keeping_score):
                    if self.playerindex == len(self.keeping_score):
                        self.keeping_score.append(player)
                        logging.info(self.keeping_score)
                        self.playerindex += 1
                        break
                    elif name in self.keeping_score[self.playerindex]:
                        self.keeping_score[self.playerindex][1] += 1
                        logging.info(self.keeping_score)
                        self.playerindex += 1
                        break
                    else:
                        logging.info("Player not found, iterating again")
                        self.playerindex += 1
                self.playerindex = 0
                self.correct = True
                self.current_question += 1
                index += 1
                if self.current_question < len(self.current_quiz):
                    message += "{}) Here is your question from the section '{}': {} ({}-{})".format(self.current_quiz[index][0], self.current_quiz[index][1], self.current_quiz[index][3], self.current_quiz[index][5], self.current_quiz[index][2])
                    return message
                else:
                    self.awaiting_response = False
                    self.finishedQuiz = True
                    self.quiztime = time.time() - self.quizstop
                    self.quiztime = time.strftime("%M:%Ss", time.gmtime(self.quiztime))
                    message += "Finished quiz! Generating results\nTime taken: {}\nScore Results-\n".format(self.quiztime)
                    self.quiztime = 0
                    self.keeping_score = sorted(self.keeping_score, key = lambda x: int(x[1]), reverse=True)
                    for player in self.keeping_score:
                        message += "{}: {}\n".format(player[0],[player[1]])
                    return message
            else:
                logging.info("Got incorrect answer %s" % (answer))
        else:
            logging.info("Failed to determine type of answer. (Expected str or list)")