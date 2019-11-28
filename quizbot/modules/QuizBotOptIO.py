# opt in and out of different events on quizbot

import sqlite3, logging

class QuizBotOptIO():
    def __init__(self, sender_name, text, groupid, name, handler):
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
        else:
            self.response = "Incorrect usage, expected - !opt <in|out>"
            