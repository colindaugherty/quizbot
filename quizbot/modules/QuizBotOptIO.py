# opt in and out of different events on quizbot

import sqlite3, logging

class QuizBotOptIO():
    def __init__(self, sender_name, text, botid, groupid, name):
        text = text.replace("!opt ", "")
        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        text = text.split()
        sender_name = sender_name.lower()
        sender_name = sender_name.replace(" ", "_")
        user_list = []
        if 0 <= 1 < len(text):
            if text[0] == "in":
                if text[1] == "newsroom":
                    t = (sender_name, botid, groupid)
                    c.execute("SELECT user FROM opt WHERE (user=? AND botid=? AND groupid=?)", (t))
                    userCheck = c.fetchone()
                    logging.info(userCheck)
                    if userCheck == None or None in userCheck:
                        insertvalues = [(name, botid, groupid, sender_name, "true", "false")]
                        c.executemany("INSERT INTO opt (name, botid, groupid, user, newsroom, elimination) VALUES (?,?,?,?,?,?)", insertvalues)
                        t = (botid, groupid)
                        for row in c.execute("SELECT user FROM opt WHERE (botid=? AND groupid=?)", (t)):
                            user_list.append(row)
                        logging.info(user_list)
                        logging.info("user_list is above me.")
                        self.response = "{} has opted in to newsroom".format(sender_name)
                        conn.commit()
                        conn.close()
                    else:
                        logging.info("Inside the else block of opting in to newsroom")
                        insertvalues = [(name, botid, groupid, sender_name)]
                        c.execute("UPDATE opt SET newsroom = 'true' WHERE (name=?, botid=?, groupid=?, user=?)", insertvalues)
                        t = (botid, groupid)
                        for row in c.execute("SELECT user FROM opt WHERE (botid=? AND groupid=?)", (t)):
                            user_list.append(row)
                        logging.info(user_list)
                        logging.info("user_list is above me.")
                        self.response = "{} has opted in to newsroom".format(sender_name)
                        conn.commit()
                        conn.close()
                elif text[1] == "elimination":
                    t = (sender_name, botid, groupid)
                    c.execute("SELECT user FROM opt WHERE (user=? AND botid=? AND groupid=?)", (t))
                    userCheck = c.fetchone()
                    logging.info(userCheck)
                    if userCheck == None or None in userCheck:
                        insertvalues = [(name, botid, groupid, sender_name, "false", "true")]
                        c.executemany("INSERT INTO opt (name, botid, groupid, user, newsroom, elimination) VALUES (?,?,?,?,?,?)", insertvalues)
                        t = (botid, groupid)
                        for row in c.execute("SELECT user FROM opt WHERE (botid=? AND groupid=?)", (t)):
                            user_list.append(row)
                        logging.info(user_list)
                        logging.info("user_list is above me.")
                        self.response = "{} has opted in to elimination".format(sender_name)
                        conn.commit()
                        conn.close()
                    else:
                        logging.info("Inside the else block of opting in to elimination")
                        insertvalues = [(name, botid, groupid, sender_name)]
                        c.execute("UPDATE opt SET elimination = 'true' WHERE (name=?, botid=?, groupid=?, user=?)", insertvalues)
                        t = (botid, groupid)
                        for row in c.execute("SELECT user FROM opt WHERE (botid=? AND groupid=?)", (t)):
                            user_list.append(row)
                        logging.info(user_list)
                        logging.info("user_list is above me.")
                        self.response = "{} has opted in to elimination".format(sender_name)
                        conn.commit()
                        conn.close()
                else:
                    self.response = "Can't opt into {}, doesn't exist!".format(text[1])
            elif text[0] == "out":
                if text[1] == "newsroom":
                    t = (sender_name, botid, groupid)
                    c.execute("SELECT user FROM opt WHERE (user=? AND botid=? AND groupid=?)", (t))
                    userCheck = c.fetchone()
                    logging.info(userCheck)
                    if userCheck == None or None in userCheck:
                        insertvalues = [(name, botid, groupid, sender_name, "false", "false")]
                        c.executemany("INSERT INTO opt (name, botid, groupid, user, newsroom, elimination) VALUES (?,?,?,?,?,?)", insertvalues)
                        t = (botid, groupid)
                        for row in c.execute("SELECT user FROM opt WHERE (botid=? AND groupid=?)", (t)):
                            user_list.append(row)
                        logging.info(user_list)
                        logging.info("user_list is above me.")
                        self.response = "{} has opted out of newsroom".format(sender_name)
                        conn.commit()
                        conn.close()
                    else:
                        logging.info("Inside the else block of opting out of newsroom")
                        insertvalues = [(name, botid, groupid, sender_name)]
                        c.execute("UPDATE opt SET newsroom = 'false' WHERE (name=?, botid=?, groupid=?, user=?)", insertvalues)
                        t = (botid, groupid)
                        for row in c.execute("SELECT user FROM opt WHERE (botid=? AND groupid=?)", (t)):
                            user_list.append(row)
                        logging.info(user_list)
                        logging.info("user_list is above me.")
                        self.response = "{} has opted out of newsroom".format(sender_name)
                        conn.commit()
                        conn.close()
                elif text[1] == "elimination":
                    t = (sender_name, botid, groupid)
                    c.execute("SELECT user FROM opt WHERE (user=? AND botid=? AND groupid=?)", (t))
                    userCheck = c.fetchone()
                    logging.info(userCheck)
                    if userCheck == None or None in userCheck:
                        insertvalues = [(name, botid, groupid, sender_name, "false", "false")]
                        c.executemany("INSERT INTO opt (name, botid, groupid, user, newsroom, elimination) VALUES (?,?,?,?,?,?)", insertvalues)
                        t = (botid, groupid)
                        for row in c.execute("SELECT user FROM opt WHERE (botid=? AND groupid=?)", (t)):
                            user_list.append(row)
                        logging.info(user_list)
                        logging.info("user_list is above me.")
                        self.response = "{} has opted out of elimination".format(sender_name)
                        conn.commit()
                        conn.close()
                    else:
                        logging.info("Inside the else block of opting out of elimination")
                        insertvalues = [(name, botid, groupid, sender_name)]
                        c.execute("UPDATE opt SET elimination = 'false' WHERE (name=?, botid=?, groupid=?, user=?)", insertvalues)
                        t = (botid, groupid)
                        for row in c.execute("SELECT user FROM opt WHERE (botid=? AND groupid=?)", (t)):
                            user_list.append(row)
                        logging.info(user_list)
                        logging.info("user_list is above me.")
                        self.response = "{} has opted out of elimination".format(sender_name)
                        conn.commit()
                        conn.close()
                else:
                    self.response = "Can't opt into {}, doesn't exist!".format(text[1])
            else:
                self.response = "Incorrect usage, expected - !opt <in|out> <newsroom|elimination>"
        elif text[0] == "in":
            t = (sender_name, botid, groupid)
            c.execute("SELECT user FROM opt WHERE (user=? AND botid=? AND groupid=?)", (t))
            userCheck = c.fetchone()
            logging.info(userCheck)
            if userCheck == None or None in userCheck:
                insertvalues = [(name, botid, groupid, sender_name, "true", "true")]
                c.executemany("INSERT INTO opt (name, botid, groupid, user, newsroom, elimination) VALUES (?,?,?,?,?,?)", insertvalues)
                t = (botid, groupid)
                for row in c.execute("SELECT user FROM opt WHERE (botid=? AND groupid=?)", (t)):
                    user_list.append(row)
                logging.info(user_list)
                logging.info("user_list is above me.")
                self.response = "{} has opted in to newsroom and elimination".format(sender_name)
                conn.commit()
                conn.close()
            else:
                logging.info("Inside the else block of opting in to newsroom and elimination")
                insertvalues = [(name, botid, groupid, sender_name)]
                c.execute("UPDATE opt SET newsroom = 'true', elimination = 'true' WHERE (name=?, botid=?, groupid=?, user=?)", insertvalues)
                t = (botid, groupid)
                for row in c.execute("SELECT user FROM opt WHERE (botid=? AND groupid=?)", (t)):
                    user_list.append(row)
                logging.info(user_list)
                logging.info("user_list is above me.")
                self.response = "{} has opted in to newsroom and elimination".format(sender_name)
                conn.commit()
                conn.close()
        elif text[0] == "out":
            t = (sender_name, botid, groupid)
            c.execute("SELECT user FROM opt WHERE (user=? AND botid=? AND groupid=?)", (t))
            userCheck = c.fetchone()
            logging.info(userCheck)
            if userCheck == None or None in userCheck:
                insertvalues = [(name, botid, groupid, sender_name, "false", "false")]
                c.executemany("INSERT INTO opt (name, botid, groupid, user, newsroom, elimination) VALUES (?,?,?,?,?,?)", insertvalues)
                t = (botid, groupid)
                for row in c.execute("SELECT user FROM opt WHERE (botid=? AND groupid=?)", (t)):
                    user_list.append(row)
                logging.info(user_list)
                logging.info("user_list is above me.")
                self.response = "{} has opted out of newsroom and elimination".format(sender_name)
                conn.commit()
                conn.close()
            else:
                logging.info("Inside the else block of opting out of newsroom and elimination")
                insertvalues = [(name, botid, groupid, sender_name)]
                c.execute("UPDATE opt SET newsroom = 'false', elimination = 'false' WHERE (name=?, botid=?, groupid=?, user=?)", insertvalues)
                t = (botid, groupid)
                for row in c.execute("SELECT user FROM opt WHERE (botid=? AND groupid=?)", (t)):
                    user_list.append(row)
                logging.info(user_list)
                logging.info("user_list is above me.")
                self.response = "{} has opted out of newsroom and elimination".format(sender_name)
                conn.commit()
                conn.close()
        else:
            self.response = "Incorrect usage, expected - !opt <in|out>"
            