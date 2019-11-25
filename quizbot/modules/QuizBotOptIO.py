# opt in and out of different events on quizbot

import sqlite3, logging

class QuizBotOptIO():
    def __init__(self, sender_name, text, botid, groupid, name, handler):
        text = text.replace("!opt ", "")
        text = text.split()
        sender_name = sender_name.lower()
        sender_name = sender_name.replace(" ", "_")
        if 0 <= 1 < len(text):
            if text[0] == "in":
                if text[1] == "newsroom":
                    data = {"name" : name, "groupid" : groupid, "table" : "opt", "data" : [name, groupid]}
                    userCheck = handler.do("select", data)
                    if userCheck == None or sender_name not in userCheck:
                        data = {"name" : name, "groupid" : groupid, "table" : "opt", "data" : [name, groupid, sender_name, "true", "false"]}
                        updated = handler.do("insert", data)
                        if updated == True:
                            self.response = f"{sender_name} has opted into newsroom"
                        else:
                            self.response = updated
                    elif sender_name in userCheck:
                        data = {"name" : name, "groupid" : groupid, "table" : ["opt", "newsroom"], "data" : ["true", name, groupid, sender_name]}
                        updated = handler.do("update", data)
                        if updated == True:
                            self.response = f"{sender_name} has opted into newsroom"
                        else:
                            self.response = updated
                elif text[1] == "elimination":
                    data = {"name" : name, "groupid" : groupid, "table" : "opt", "data" : [name, groupid]}
                    userCheck = handler.do("select", data)
                    if userCheck == None or sender_name not in userCheck:
                        data = {"name" : name, "groupid" : groupid, "table" : "opt", "data" : [name, groupid, sender_name, "false", "true"]}
                        updated = handler.do("insert", data)
                        if updated == True:
                            self.response = f"{sender_name} has opted into newsroom"
                        else:
                            self.response = updated
                    elif sender_name in userCheck:
                        data = {"name" : name, "groupid" : groupid, "table" : ["opt", "elimination"], "data" : ["true", name, groupid, sender_name]}
                        updated = handler.do("update", data)
                        if updated == True:
                            self.response = f"{sender_name} has opted into newsroom"
                        else:
                            self.response = updated
                else:
                    self.response = f"Can't opt into {text[1]}, doesn't exist!"
            elif text[0] == "out":
                if text[1] == "newsroom":
                    data = {"name" : name, "groupid" : groupid, "table" : "opt", "data" : [name, groupid]}
                    userCheck = handler.do("select", data)
                    if userCheck == None or sender_name not in userCheck:
                        data = {"name" : name, "groupid" : groupid, "table" : "opt", "data" : [name, groupid, sender_name, "false", "false"]}
                        updated = handler.do("insert", data)
                        if updated == True:
                            self.response = f"{sender_name} has opted out of newsroom"
                        else:
                            self.response = updated
                    elif sender_name in userCheck:
                        data = {"name" : name, "groupid" : groupid, "table" : ["opt", "newsroom"], "data" : ["false", name, groupid, sender_name]}
                        updated = handler.do("update", data)
                        if updated == True:
                            self.response = f"{sender_name} has opted out of newsroom"
                        else:
                            self.response = updated
                    # t = (sender_name, botid, groupid)
                    # c.execute("SELECT users FROM opt WHERE (users=? AND botid=? AND groupid=?)", (t))
                    # userCheck = c.fetchone()
                    # logging.info(userCheck)
                    # if userCheck == None or None in userCheck:
                    #     insertvalues = [(name, botid, groupid, sender_name, "false", "false")]
                    #     c.executemany("INSERT INTO opt (name, botid, groupid, users, newsroom, elimination) VALUES (?,?,?,?,?,?)", insertvalues)
                    #     t = (botid, groupid)
                    #     for row in c.execute("SELECT users FROM opt WHERE (botid=? AND groupid=?)", (t)):
                    #         user_list.append(row)
                    #     logging.info(user_list)
                    #     logging.info("user_list is above me.")
                    #     self.response = "{} has opted out of newsroom".format(sender_name)
                    #     conn.commit()
                    #     conn.close()
                    # else:
                    #     logging.info("Inside the else block of opting out of newsroom")
                    #     insertvalues = [(name, botid, groupid, sender_name)]
                    #     logging.info(c.executemany("UPDATE opt SET newsroom == 'false' WHERE (name=? AND botid=? AND groupid=? AND users=?)", insertvalues))
                    #     c.executemany("UPDATE opt SET newsroom = 'false' WHERE (name=? AND botid=? AND groupid=? AND users=?)", insertvalues)
                    #     t = (botid, groupid)
                    #     for row in c.execute("SELECT users FROM opt WHERE (botid=? AND groupid=?)", (t)):
                    #         user_list.append(row)
                    #     logging.info(user_list)
                    #     logging.info("user_list is above me.")
                    #     self.response = "{} has opted out of newsroom".format(sender_name)
                    #     conn.commit()
                    #     conn.close()
                    #     logging.info("Finished the else block of opting out of newsroom")
                elif text[1] == "elimination":
                    data = {"name" : name, "groupid" : groupid, "table" : "opt", "data" : [name, groupid]}
                    userCheck = handler.do("select", data)
                    if userCheck == None or sender_name not in userCheck:
                        data = {"name" : name, "groupid" : groupid, "table" : "opt", "data" : [name, groupid, sender_name, "false", "false"]}
                        updated = handler.do("insert", data)
                        if updated == True:
                            self.response = f"{sender_name} has opted out of elimination"
                        else:
                            self.response = updated
                    elif sender_name in userCheck:
                        data = {"name" : name, "groupid" : groupid, "table" : ["opt", "elimination"], "data" : ["false", name, groupid, sender_name]}
                        updated = handler.do("update", data)
                        if updated == True:
                            self.response = f"{sender_name} has opted out of elimination"
                        else:
                            self.response = updated
                    # t = (sender_name, botid, groupid)
                    # c.execute("SELECT users FROM opt WHERE (users=? AND botid=? AND groupid=?)", (t))
                    # userCheck = c.fetchone()
                    # logging.info(userCheck)
                    # if userCheck == None or None in userCheck:
                    #     insertvalues = [(name, botid, groupid, sender_name, "false", "false")]
                    #     c.executemany("INSERT INTO opt (name, botid, groupid, users, newsroom, elimination) VALUES (?,?,?,?,?,?)", insertvalues)
                    #     t = (botid, groupid)
                    #     for row in c.execute("SELECT users FROM opt WHERE (botid=? AND groupid=?)", (t)):
                    #         user_list.append(row)
                    #     logging.info(user_list)
                    #     logging.info("user_list is above me.")
                    #     self.response = "{} has opted out of elimination".format(sender_name)
                    #     conn.commit()
                    #     conn.close()
                    # else:
                    #     logging.info("Inside the else block of opting out of elimination")
                    #     insertvalues = [(name, botid, groupid, sender_name)]
                    #     c.executemany("UPDATE opt SET elimination = 'false' WHERE (name=? AND botid=? AND groupid=? AND users=?)", insertvalues)
                    #     t = (botid, groupid)
                    #     for row in c.execute("SELECT users FROM opt WHERE (botid=? AND groupid=?)", (t)):
                    #         user_list.append(row)
                    #     logging.info(user_list)
                    #     logging.info("user_list is above me.")
                    #     self.response = "{} has opted out of elimination".format(sender_name)
                    #     conn.commit()
                    #     conn.close()
                else:
                    self.response = "Can't opt out of {}, doesn't exist!".format(text[1])
            else:
                self.response = "Incorrect usage, expected - !opt <in|out> <newsroom|elimination>"
        elif text[0] == "in":
            data = {"name" : name, "groupid" : groupid, "table" : "opt", "data" : [name, groupid]}
            userCheck = handler.do("select", data)
            if userCheck == None or sender_name not in userCheck:
                data = {"name" : name, "groupid" : groupid, "table" : "opt", "data" : [name, groupid, sender_name, "true", "true"]}
                updated = handler.do("insert", data)
                if updated == True:
                    self.response = f"{sender_name} has opted into newsroom"
                else:
                    self.response = updated
            elif sender_name in userCheck:
                data = {"name" : name, "groupid" : groupid, "table" : ["opt", "newsroom"], "data" : ["true", name, groupid, sender_name]}
                updatedone = handler.do("update", data)
                data = {"name" : name, "groupid" : groupid, "table" : ["opt", "elimination"], "data" : ["true", name, groupid, sender_name]}
                updatedtwo = handler.do("update", data)
                if updatedone == True and updatedtwo == True:
                    self.response = f"{sender_name} has opted into newsroom"
                else:
                    self.response = f"Operation One Finished - {updatedone}\nOperation Two Finished - {updatedtwo}" 
            # t = (sender_name, botid, groupid)
            # c.execute("SELECT users FROM opt WHERE (users=? AND botid=? AND groupid=?)", (t))
            # userCheck = c.fetchone()
            # logging.info(userCheck)
            # if userCheck == None or None in userCheck:
            #     insertvalues = [(name, botid, groupid, sender_name, "true", "true")]
            #     c.executemany("INSERT INTO opt (name, botid, groupid, users, newsroom, elimination) VALUES (?,?,?,?,?,?)", insertvalues)
            #     t = (botid, groupid)
            #     for row in c.execute("SELECT users FROM opt WHERE (botid=? AND groupid=?)", (t)):
            #         user_list.append(row)
            #     logging.info(user_list)
            #     logging.info("user_list is above me.")
            #     self.response = "{} has opted in to newsroom and elimination".format(sender_name)
            #     conn.commit()
            #     conn.close()
            # else:
            #     logging.info("Inside the else block of opting in to newsroom and elimination")
            #     insertvalues = [(name, botid, groupid, sender_name)]
            #     c.executemany("UPDATE opt SET newsroom = 'true', elimination = 'true' WHERE (name=? AND botid=? AND groupid=? AND users=?)", insertvalues)
            #     t = (botid, groupid)
            #     for row in c.execute("SELECT users FROM opt WHERE (botid=? AND groupid=?)", (t)):
            #         user_list.append(row)
            #     logging.info(user_list)
            #     logging.info("user_list is above me.")
            #     self.response = "{} has opted in to newsroom and elimination".format(sender_name)
            #     conn.commit()
            #     conn.close()
        elif text[0] == "out":
            data = {"name" : name, "groupid" : groupid, "table" : "opt", "data" : [name, groupid]}
            userCheck = handler.do("select", data)
            if userCheck == None or sender_name not in userCheck:
                data = {"name" : name, "groupid" : groupid, "table" : "opt", "data" : [name, groupid, sender_name, "false", "false"]}
                updated = handler.do("insert", data)
                if updated == True:
                    self.response = f"{sender_name} has opted into newsroom"
                else:
                    self.response = updated
            elif sender_name in userCheck:
                data = {"name" : name, "groupid" : groupid, "table" : ["opt", "newsroom"], "data" : ["false", name, groupid, sender_name]}
                updatedone = handler.do("update", data)
                data = {"name" : name, "groupid" : groupid, "table" : ["opt", "elimination"], "data" : ["false", name, groupid, sender_name]}
                updatedtwo = handler.do("update", data)
                if updatedone == True and updatedtwo == True:
                    self.response = f"{sender_name} has opted into newsroom"
                else:
                    self.response = f"Operation One Finished - {updatedone}\nOperation Two Finished - {updatedtwo}" 
            # t = (sender_name, botid, groupid)
            # c.execute("SELECT users FROM opt WHERE (users=? AND botid=? AND groupid=?)", (t))
            # userCheck = c.fetchone()
            # logging.info(userCheck)
            # logging.info("userCheck is {} and whether or not it is a tuple: {}".format(userCheck, isinstance(userCheck, tuple)))
            # if userCheck == None or None in userCheck:
            #     insertvalues = [(name, botid, groupid, sender_name, "false", "false")]
            #     c.executemany("INSERT INTO opt (name, botid, groupid, users, newsroom, elimination) VALUES (?,?,?,?,?,?)", insertvalues)
            #     t = (botid, groupid)
            #     for row in c.execute("SELECT users FROM opt WHERE (botid=? AND groupid=?)", (t)):
            #         user_list.append(row)
            #     logging.info(user_list)
            #     logging.info("user_list is above me.")
            #     self.response = "{} has opted out of newsroom and elimination".format(sender_name)
            #     conn.commit()
            #     conn.close()
            # elif isinstance(userCheck, tuple):
            #     logging.info("Inside the else block of opting out of newsroom and elimination")
            #     insertvalues = [(name, botid, groupid, sender_name)]
            #     c.executemany("UPDATE opt SET newsroom = 'false', elimination = 'false' WHERE (name=? AND botid=? AND groupid=? AND users=?)", insertvalues)
            #     t = (botid, groupid)
            #     for row in c.execute("SELECT users FROM opt WHERE (botid=? AND groupid=?)", (t)):
            #         user_list.append(row)
            #     logging.info(user_list)
            #     logging.info("user_list is above me.")
            #     self.response = "{} has opted out of newsroom and elimination".format(sender_name)
            #     conn.commit()
            #     conn.close()
            # else:
            #     logging.info("Failed")
        else:
            self.response = "Incorrect usage, expected - !opt <in|out>"
            