import sqlite3, logging

class QuizBotSetMemeSource:
    def __init__(self, botid, groupid):
        conn = sqlite3.connect('config.db')
        c = conn.cursor()
        t = (botid, groupid)
        memesource = []
        for row in c.execute("SELECT subreddit FROM memesource WHERE (botid=? AND groupid=?)", (t)):
            memesource.append(row[0])
        logging.info(f"Inside _getmemesource: memesource should be populated here it is- {memesource}")
        conn.commit()
        conn.close()

        self.response = memesource