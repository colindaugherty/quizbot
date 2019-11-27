# class to handle authenticating users

import logging

class QuizBotAuthenticateUser:
    def __init__(self, sender_name, text, name, groupid, handler):
        text = text.strip()
        if "!authenticate" in text:
            text = text.replace("!authenticate ", "")
            auth = "enable"
        elif "!deauthenticate" in text:
            text = text.replace("!deauthenticate ", "")
            auth = "disable"
        text = text.split()
        sender_name = sender_name.lower()
        sender_name = sender_name.replace(" ", "_")
        print(text)
        print(sender_name)
        data = {"name" : name, "groupid" : groupid, "table" : "authenticate", "data" : [name, groupid]}
        userCheck = handler.do("select", data)
        if userCheck == None:
            if len(text) == 2 and text[0] == name and int(text[1]) == groupid:
                print(f"Text - {text}\nName - {name}\nGroupId - {groupid}\nText[0] - {text[0]}\nText[1] (int) - {int(text[1])}")
                data = {"name" : name, "groupid" : groupid, "table" : "authenticate", "data" : [name, groupid, sender_name]}
                inserted = handler.do("insert", data)
                if inserted == True:
                    self.response = f"{sender_name} has been authenticated. Since there is now at least one in the database, this method is no longer available."
                else:
                    self.response = f"Something weird happened, here's my response - {inserted}"
            else:
                if auth == "disable":
                    self.response = "Failed - There are no authenticated users left"
                else:
                    self.response = "Please include bot_name and group_id"
        elif isinstance(userCheck, list):
            if sender_name in userCheck:
                if auth == "enable":
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
                                message += f"\nHad trouble adding {user} - if the error persists let the developer know.\n{confirm}"
                        else:
                            message += f"\nUser: {user}, is already authenticated"
                    logging.info(f"A list of the users I just authenticated - {users}")
                    self.response = message
                elif auth == "disable":
                    users = []
                    message = "Removed people -"
                    for user in text:
                        if user in userCheck:
                            data = {"name" : name, "groupid" : groupid, "table" : "authenticate", "data" : [name, groupid, user]}
                            confirm = handler.do("delete", data)
                            if confirm == True:
                                users.append(user)
                                message += f"\n{user}"
                            else:
                                message += f"\nHad trouble removing {user} - if the error persists let the developer know.\n{confirm}"
                        else:
                            message += f"\nUser: {user}, isn't authenticated"
                    logging.info(f"A list of users I just deauthenticated - {users}")
                    self.response = message
            else:
                self.response = f"Sorry {sender_name}, this method is only availble to authenticated members."
        else:
            self.response = f"userCheck was something unexpected, here it is - {userCheck}"