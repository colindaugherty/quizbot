# class for returning stats

import logging, sqlite3

class QuizBotReturnStats:
    def __init__(self, botname, groupid):
        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        t = (botname, groupid)
        message = "Stats for the group with bot {}:\n".format(botname)
        c.execute("SELECT requests FROM stats WHERE name=? AND groupid=?", t)
        requests = c.fetchone()
        message += "Total requests to {}: {}\n".format(botname, requests[0])
        c.execute("SELECT responses FROM stats WHERE name=? AND groupid=?", t)
        responses = c.fetchone()
        message += "Total times {} responded: {}\n".format(botname, responses[0])
        c.execute("SELECT FredResponses FROM stats WHERE name=? AND groupid=?", t)
        FredResponses = c.fetchone()
        message += "Total times Fred has responded to his name: {}\n".format(FredResponses[0])
        c.execute("SELECT TotalMessages FROM stats WHERE name=? AND groupid=?", t)
        TotalMessages = c.fetchone()
        message += "Total messages in this group: {}\n".format(TotalMessages[0])
        message += "Finished stats!"
        self.response = message