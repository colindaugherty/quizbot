# update by group config

import sqlite3, logging

class QuizBotUpdateConfig:
    def __init__(self, authenticatedusers, text, botname, groupid, sender_name, handler):
        sender_name = sender_name.lower()
        sender_name = sender_name.replace(" ", "_")
        logging.info(text)
        if sender_name in authenticatedusers:
            if "!config subreddit" in text:
                text = text.replace("!config subreddit", "")
                if "add" in text:
                    text = text.replace("add", "")
                    text = text.split()
                    message = "Result - \n"
                    for subreddit in text:
                        data = {"name" : botname, "groupid" : groupid, "table" : "memesource", "data" : [botname, groupid, subreddit]}
                        confirm = handler.do("insert", data)
                        if confirm == True:
                            message += f"Added {subreddit}\n"
                        else:
                            message += f"Failed to add {subreddit}, if the error persists, let the developer know.\n{confirm}\n"
                    self.response = message
                elif "delete" in text:
                    text = text.replace("delete", "")
                    text = text.split()
                    message = "Result - \n"
                    for subreddit in text:
                        data = {"name" : botname, "groupid" : groupid, "table" : "memesource", "data" : [botname, groupid, subreddit]}
                        confirm = handler.do("insert", data)
                        if confirm == True:
                            message += f"Removed {subreddit}\n"
                        else:
                            message += f"Failed to remove {subreddit}, if the error persists, let the developer know.\n{confirm}\n"
                    self.response = message
                else:
                    text = text.split()
                    if len(text) == 2:
                        data = {"name" : botname, "groupid" : groupid, "table" : "memesource", "data" : [botname, groupid]}
                        sourceList = handler.do("select", data)
                        message = "Current subreddits enabled to pull from - \n"
                        for subreddit in sourceList:
                            message += f"{subreddit}\n"
                        self.response = message
                    else:
                        self.response = f"Improper usage! Expected add|delete not {text[3]}"
            elif "!config allownsfw" in text:
                text = text.replace("!config allownsfw")
                if "true" in text:
                    data = {"name" : botname, "groupid" : groupid, "table" : ["config", "allownsfw"], "data" : ["true", botname, groupid]}
                    confirm = handler.do("update", data)
                    if confirm == True:
                        self.response = "allownsfw updated to True"
                    else:
                        self.response = f"Error - \n{confirm}"
                elif "false" in text:
                    data = {"name" : botname, "groupid" : groupid, "table" : ["config", "allownsfw"], "data" : ["false", botname, groupid]}
                    confirm = handler.do("update", data)
                    if confirm == True:
                        self.response = "allownsfw updated to False"
                    else:
                        self.response = f"Error - \n{confirm}"
                else:
                    text = text.split()
                    self.response = f"Expected true|false not {text[1]}"
            elif "!config allowrepost" in text:
                if "true" in text:
                    data = {"name" : botname, "groupid" : groupid, "table" : ["config", "allowrepost"], "data" : ["true", botname, groupid]}
                    confirm = handler.do("update", data)
                    if confirm == True:
                        self.response = "allowrepost updated to True"
                    else:
                        self.response = f"Error - \n{confirm}"
                elif "false" in text:
                    data = {"name" : botname, "groupid" : groupid, "table" : ["config", "allowrepost"], "data" : ["false", botname, groupid]}
                    confirm = handler.do("update", data)
                    if confirm == True:
                        self.response = "allowrepost updated to False"
                    else:
                        self.response = f"Error - \n{confirm}"
                else:
                    text = text.split()
                    self.response = f"Expected true|false not {text[1]}"
            else:
                text = text.split()
                self.response = f"I didn't find that config ({text[1]}), perhaps you mispelled it?"
        else:
            self.response = f"{sender_name}, this is only for authenticated users."