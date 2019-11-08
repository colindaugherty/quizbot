# update by group config

import sqlite3, logging

class QuizBotUpdateConfig:
    def __init__(self, authenticatedusers, botname, botid, groupid, sender_name, currentnsfw, currentrepost, currentmemesource, text):
        sender_name = sender_name.lower()
        sender_name = sender_name.replace(" ", "_")
        if sender_name in authenticatedusers:
            conn = sqlite3.connect('config.db')
            c = conn.cursor()
            text = text.lower()
            what_config = ['subreddit','allownsfw','allowrepost']
            text = text.split(' ')
            logging.info(text)
            configword = text[1]
            if configword in what_config:
                if what_config[0] == configword:
                    if 0 <= 2 < len(text):
                        if text[2] == 'add':
                            if 0 <= 3 < len(text):
                                t = [(botname, botid, groupid, text[3])]
                                c.executemany("INSERT INTO memesource (name, botid, groupid, subreddit) VALUES (?,?,?,?)", t)
                                memesource = []
                                t = [(botname),]
                                for row in c.execute("SELECT subreddit FROM memesource WHERE (name=?)", (t)):
                                    memesource.append(row)
                                logging.info("Just updated memesource here it is- %s" % (memesource))    
                                conn.commit()
                                conn.close()
                                message = "Updated subreddit list, added - "
                                message += text[3]
                                self.response = message
                            else:
                                self.response = "You didn't include a subreddit!\nUsage - !config subreddit add <subreddit>"
                        elif text[2] == 'delete':
                            if 0 <= 3 < len(text):
                                t = [(text[3],botname)]
                                c.executemany("DELETE FROM memesource WHERE (subreddit=? AND name=?)", (t))
                                memesource = []
                                t = [(botname),]
                                for row in c.execute("SELECT subreddit FROM memesource WHERE (name=?)", (t)):
                                    memesource.append(row[0])
                                logging.info("Just updated memesource here it is- %s" % (memesource))    
                                conn.commit()
                                conn.close()
                                message = "Updated subreddit list, removed - "
                                message += text[3]
                                self.response = message
                            else:
                                self.response = "You didn't include a subreddit!\nUsage - !config subreddit add <subreddit>"
                        else:
                            self.response = "Incorrect usage, expected add|delete\nUsage - !config subreddit <add|delete>"
                    else:
                        message = "Current enabled subreddits to pull from -"
                        for subreddit in currentmemesource:
                            message += "\n{}".format(subreddit)
                        self.response = message
                elif what_config[1] == configword:
                    if 0 <= 2 < len(text):
                        if text[2] == 'true':
                            t = (text[2],botid,groupid)
                            c.executemany("UPDATE config SET allownsfw=? WHERE (botid=? AND groupid=?)", (t))
                            t = [(botname),]
                            c.execute("SELECT allownsfw FROM config WHERE (name=?)", (t))
                            allownsfw = c.fetchone()
                            logging.info("Just updated allownsfw, expected output is 'true', here it is- %s" % (allownsfw))
                            conn.commit()
                            conn.close()
                            message = "Updated status of allownsfw - "
                            message += text[2]
                            self.response = message
                        elif text[2] == 'false':
                            t = (text[2],botid,groupid)
                            c.executemany("UPDATE config SET allownsfw=? WHERE (botid=? AND groupid=?)", (t))
                            t = [(botname),]
                            c.execute("SELECT allownsfw FROM config WHERE (name=?)", (t))
                            allownsfw = c.fetchone()
                            logging.info("Just updated allownsfw, expected output is 'false', here it is- %s" % (allownsfw))
                            conn.commit()
                            conn.close()
                            message = "Updated status of allownsfw - "
                            message += text[2]
                            self.response = message
                        else:
                            self.response = "Incorrect usage, expected true|false\nUsage !config allownsfw <true|false>"
                    else:
                        message = "Current status of allownsfw - "
                        message += currentnsfw
                        self.response = message
                elif what_config[2] == configword:
                    if 0 <= 2 < len(text):
                        if text[2] == 'true':
                            t = (text[2],botid,groupid)
                            c.executemany("UPDATE config SET allowrepost=? WHERE (botid=? AND groupid=?)", (t))
                            t = [(botname),]
                            c.execute("SELECT allowrepost FROM config WHERE (name=?)", (t))
                            allowrepost = c.fetchone()
                            logging.info("Just updated allowrepost, expected output is 'true', here it is- %s" % (allowrepost))
                            conn.commit()
                            conn.close()
                            message = "Updated status of allowrepost - "
                            message += text[2]
                            self.response = message
                        elif text[2] == 'false':
                            t = (text[2],botid,groupid)
                            c.executemany("UPDATE config SET allowrepost=? WHERE (botid=? AND groupid=?)", (t))
                            t = [(botname),]
                            c.execute("SELECT allowrepost FROM config WHERE (name=?)", (t))
                            allowrepost = c.fetchone()
                            logging.info("Just updated allowrepost, expected output is 'false', here it is- %s" % (allowrepost))
                            conn.commit()
                            conn.close()
                            message = "Updated status of allowrepost - "
                            message += text[2]
                            self.response = message
                        else:
                            self.response = "Incorrect usage, expected true|false\nUsage !config allowrepost <true|false>"
                    else:
                        message = "Current status of allowrepost - "
                        message += currentrepost
                        self.response = message
                else:
                    self.response = "Sorry, I can't find that config! This is the config message I received-\n{}".format(text)
        else:
            self.response = "Sorry, this is only for authenticated users."