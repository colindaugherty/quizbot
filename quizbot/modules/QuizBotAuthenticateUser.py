# class to handle authenticating users

import logging

class QuizBotAuthenticateUser:
    def __init__(self, sender_name, text, name, groupid, handler):
        text = text.strip()
        text = text.replace("!authenticate ", "")
        text = text.split()
        sender_name = sender_name.lower()
        sender_name = sender_name.replace(" ", "_")
        data = {"name" : name, "groupid" : groupid, "table" : "authenticate", "data" : [name, groupid]}
        userCheck = handler.do("select", data)
        if userCheck == None:
            if len(text) == 2:
                data = {"name" : name, "groupid" : groupid, "table" : "authenticate", "data" : [name, groupid, sender_name]}
                inserted = handler.do("insert", data)
                if inserted == True:
                    self.response = f"{sender_name} has been authenticated. Since there is now at least one in the database, this method is no longer available."
                else:
                    self.response = f"Something weird happened, here's my response - {inserted}"
            else:
                self.response = "Please include bot_name and group_id"
        elif isinstance(userCheck, list):
            if sender_name in userCheck:
                users = []
                message = "Added people -"
                for user in text:
                    if user not in userCheck:
                        data = {"name" : name, "groupid" : groupid, "table" : "authenticate", "data" : [name, groupid, user]}
                        confirm = handler.do("insert", data)
                        if confirm == True:
                            users.append(user)
                            message += f"\n{user}"
                        else:
                            message += f"\nHad trouble adding {user} - if the error persists let the developer know."
                    else:
                        message += f"\nUser: {user}, is already authenticated"
                logging.info(f"A list of the users I just added - {users}")
                self.response = message
            else:
                self.response = f"Sorry {sender_name}, this method is only availble to authenticated members."
        else:
            self.response = f"userCheck was something unexpected, here it is - {userCheck}"