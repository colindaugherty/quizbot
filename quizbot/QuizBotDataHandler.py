# database handler for quizbot

import sqlite3, logging, traceback

logging.basicConfig(level=logging.DEBUG,filename='logs/data.log', filemode='w', format='QuizBot[DATA]: %(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

discord_data = "data/discord.db"
groupme_data = "data/groupme.db"

class QuizBotDataHandler:
    def __init__(self, discord=False, groupme=False):
        self.discord = discord
        self.groupme = groupme
        
        self.methods = {
            "update" : self.update,
            "insert" : self.insert,
            "delete" : self.delete,
            "selectall" : self.selectall,
            "selectone" : self.selectone,
            "select" : self.selectall,
        }

    def _setup_defaults_(self, db, c, identity):
        name = identity[0]
        groupid = identity[1]
        c.execute("""CREATE TABLE IF NOT EXISTS config
        (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, groupid int, allownsfw text, allowrepost text)
        """)
        c.execute("""CREATE TABLE IF NOT EXISTS memesource
        (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, groupid int, subreddit text)
        """)
        c.execute("""CREATE TABLE IF NOT EXISTS stats
        (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, groupid int, requests int, responses int, FredResponses int, TotalMessages int)
        """)
        c.execute("""CREATE TABLE IF NOT EXISTS authenticate
        (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, groupid int, users text)
        """)
        c.execute("""CREATE TABLE IF NOT EXISTS opt
        (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, groupid int, users text, newsroom text, elimination text)
        """)

        c.execute("SELECT * FROM config WHERE name=? AND groupid=?", identity)
        checkconfig = c.fetchone()
        c.execute("SELECT * FROM memesource WHERE name=? AND groupid=?", identity)
        checkmemesource = c.fetchone()
        c.execute("SELECT * FROM stats WHERE name=? AND groupid=?", identity)
        checkstats = c.fetchone()
        if checkconfig == None and checkmemesource == None or None in checkconfig and None in checkmemesource:
            logging.info(f"Doing default config for bot {name} in group {groupid}")
            insertvalues = [(name, groupid, 'false','false')]
            c.executemany("INSERT INTO config (name, groupid, allownsfw, allowrepost) VALUES (?,?,?,?)", insertvalues)
            insertvalues = [(name, groupid, 'all')]
            c.executemany("INSERT INTO memesource (name, groupid, subreddit) VALUES (?,?,?)", insertvalues)
            logging.info("Finished - results:\n")
            for row in c.execute("SELECT * FROM config ORDER BY id"):
                logging.info(row)
            for row in c.execute("SELECT * FROM memesource ORDER BY groupid"):
                logging.info(row)
            db.commit()
        else:
            for row in c.execute("SELECT * FROM config ORDER BY id"):
                logging.info(row)
            for row in c.execute("SELECT * FROM memesource ORDER BY groupid"):
                logging.info(row)
        logging.info("-- DOING STATS --")
        if checkstats == None or None in checkstats:
            logging.info(f"Setting up stats for bot {name} in group {groupid}")
            insertvalues = [(name, groupid, 0, 0, 0, 0)]
            c.executemany("INSERT INTO stats (name, groupid, requests, responses, FredResponses, TotalMessages) VALUES (?, ?, ?, ?, ?, ?)", insertvalues)
            for row in c.execute("SELECT * FROM stats ORDER BY groupid"):
                logging.info(row)
            db.commit()
        else:
            for row in c.execute("SELECT * FROM stats ORDER BY groupid"):
                logging.info(row)

        logging.info("Finished setting defaults")
        db.commit()
        return "Finished setting up."

    def connect(self, datafile):
        db = sqlite3.connect(datafile)
        c = db.cursor()

        return (db, c)

    def clean_up(self, db, c):
        c.close()
        db.close()

    def update(self, db, c, table, data):
        try:
            logging.info(f"Editing database with this data- {data}")
            if table == "opt":
                c.executemany("UPDATE opt SET newsroom=? AND elimination=? WHERE (name=? AND groupid=?)", [data])
                db.commit()
                self.clean_up(db, c)
                return True
            elif isinstance(table, list):
                subtable = table[1]
                if table[0] == "stats":
                    if subtable == "requests":
                        c.executemany("UPDATE stats SET requests = requests + 1 WHERE (name=? AND groupid=?)", [data])
                        db.commit()
                        self.clean_up(db, c)
                        return True
                    elif subtable == "responses":
                        c.executemany("UPDATE stats SET responses = responses + 1 WHERE (name=? AND groupid=?)", [data])
                        db.commit()
                        self.clean_up(db, c)
                        return True
                    elif subtable == "fredresponses":
                        c.executemany("UPDATE stats SET FredMessages = FredMessages + 1 WHERE (name=? AND groupid=?)", [data])
                        db.commit()
                        self.clean_up(db, c)
                        return True
                    elif subtable == "totalmessages":
                        c.executemany("UPDATE stats SET TotalMessages = TotalMessages + 1 WHERE (name=? AND groupid=?)", [data])
                        db.commit()
                        self.clean_up(db, c)
                        return True
                    else:
                        return f"Couldn't find subtable {subtable} in table {table[0]}"
                elif table[0] == "config":
                    if subtable == "allowrepost":
                        c.executemany("UPDATE config SET allowrepost = ? WHERE (name=? AND groupid=?)", [data])
                        db.commit()
                        self.clean_up(db, c)
                        return True
                    elif subtable == "allownsfw":
                        c.executemany("UPDATE config set allownsfw = ? WHERE (name=? AND groupid=?)", [data])
                        db.commit()
                        self.clean_up(db, c)
                        return True
                    else:
                        return f"Couldn't find subtable {subtable} in table {table[0]}"
                else:
                    return f"You included a list for an incompatible table, {table}\nCompatible tables: config, stats"
            else:
                return f"This should really only be used for stats, config, and opt, it was used for {table}"
            db.commit()
            self.clean_up(db, c)
            logging.info("Finished editing database.")
        except Exception as e:
            self.clean_up(db, c)
            print(traceback.format_exc())
            return f"Encountered error - {e}\n"

    def insert(self, db, c, table, data):
        try:
            if table == "memesource":
                c.executemany("INSERT INTO memesource (name, groupid, subreddit) VALUES (?, ?, ?)", [data])
                db.commit()
                self.clean_up(db, c)
                return True
            elif table == "authenticate":
                c.executemany("INSERT INTO authenticate (name, groupid, users) VALUES (?, ?, ?)", [data])
                db.commit()
                self.clean_up(db, c)
                return True
            elif table == "opt":
                c.executemany("INSERT INTO opt (name, groupid, users, newsroom, elimination) VALUES (?, ?, ?, ?, ?)", [data])
                db.commit()
                self.clean_up(db, c)
                return True
            else:
                return f"This should really only be used for adding memesource and authenticated/new opt users, however, it was used for {table}"
        except Exception as e:
            self.clean_up(db, c)
            return f"Encountered error - {e}"

    def delete(self, db, c, table, data):
        try:
            if table == "memesource":
                c.executemany("DELETE FROM memesource WHERE (name=? AND groupid=? AND subreddit=?)", [data])
                db.commit()
                self.clean_up(db, c)
                return True
            elif table == "authenticate":
                c.executemany("DELETE FROM authenticate WHERE (name=? AND groupid=? AND users=?)", [data])
            else:
                return f"This should really only be used for deleting memesource and authenticated users, it was used for {table}"
        except Exception as e:
            self.clean_up(db, c)
            return f"Encountered error - {e}"

    def selectone(self, db, c, table, data):
        try:
            if isinstance(table, list):
                subtable = table[1]
                if table[0] == "config":
                    if subtable == "allowrepost":
                        c.execute("SELECT allowrepost FROM config WHERE (name=? AND groupid=?)", data)
                        data = c.fetchone()
                        return data[0]
                    elif subtable == "allownsfw":
                        c.execute("SELECT allownsfw FROM config WHERE (name=? AND groupid=?)", data)
                        data = c.fetchone()
                        return data[0]
                    else:
                        return f"Subtable not found, was given {subtable}"
                elif table[0] == "stats":
                    if subtable == "responses":
                        c.execute("SELECT responses FROM stats WHERE (name=? AND groupid=?)", data)
                        data = c.fetchone()
                        return data[0]
                    elif subtable == "requests":
                        c.execute("SELECT requests FROM stats WHERE (name=? AND groupid=?)", data)
                        data = c.fetchone()
                        return data[0]
                    elif subtable == "fredresponses":
                        c.execute("SELECT FredResponses FROM stats WHERE (name=? AND groupid=?)", data)
                        data = c.fetchone()
                        return data[0]
                    elif subtable == "totalmessages":
                        c.execute("SELECT TotalMessages FROM stats WHERE (name=? AND groupid=?)", data)
                        data = c.fetchone()
                        return data[0]
                    else:
                        return f"Subtable not found, was given {subtable}"
                else:
                    return f"Table {table} is not supported for lists.\nCompatiable tables are: config, stats"
            elif table == "memesource":
                c.execute("SELECT subreddit FROM memesource WHERE (name=? AND groupid=?)", data)
                data = c.fetchone()
                return data[0]
            elif table == "authenticate":
                c.execute("SELECT users FROM authenticate WHERE (name=? AND groupid=?)", data)
                data = c.fetchone()
                return data[0]
            elif table == "opt":
                c.execute("SELECT users FROM opt WHERE (name=? AND groupid=?)", data)
                data = c.fetchone()
                return data[0]
        except Exception as e:
            self.clean_up(db, c)
            return f"Encountered error - {e}"

    def selectall(self, db, c, table, data):
        try:
            if isinstance(table, list):
                subtable = table[1]
                if table[0] == "config":
                    if subtable == "allowrepost":
                        c.execute("SELECT allowrepost FROM config WHERE (name=? AND groupid=?)", data)
                        data = c.fetchall()
                        return data
                    elif subtable == "allownsfw":
                        c.execute("SELECT allownsfw FROM config WHERE (name=? AND groupid=?)", data)
                        data = c.fetchall()
                        return data
                    else:
                        return f"Subtable not found, was given {subtable}"
                elif table[0] == "stats":
                    if subtable == "responses":
                        c.execute("SELECT responses FROM stats WHERE (name=? AND groupid=?)", data)
                        data = c.fetchall()
                        return data
                    elif subtable == "requests":
                        c.execute("SELECT requests FROM stats WHERE (name=? AND groupid=?)", data)
                        data = c.fetchall()
                        return data
                    elif subtable == "fredresponses":
                        c.execute("SELECT FredResponses FROM stats WHERE (name=? AND groupid=?)", data)
                        data = c.fetchall()
                        return data
                    elif subtable == "totalmessages":
                        c.execute("SELECT TotalMessages FROM stats WHERE (name=? AND groupid=?)", data)
                        data = c.fetchall()
                        return data
                    else:
                        return f"Subtable not found, was given {subtable}"
                else:
                    return f"Table {table} is not supported for lists.\nCompatiable tables are: config, stats"
            elif table == "memesource":
                c.execute("SELECT subreddit FROM memesource WHERE (name=? AND groupid=?)", data)
                data = c.fetchall()
                return data
            elif table == "authenticate":
                c.execute("SELECT users FROM authenticate WHERE (name=? AND groupid=?)", data)
                data = c.fetchall()
                return data
            elif table == "opt":
                c.execute("SELECT users FROM opt WHERE (name=? AND groupid=?)", data)
                data = c.fetchall()
                return data
        except Exception as e:
            self.clean_up(db, c)
            return f"Encountered error - {e}"

    def do(self, method, data):
        identity = [data["name"], data["groupid"]]
        table = data["table"]
        data = tuple(data["data"])
        if self.discord:
            db, c = self.connect(discord_data)
            method = self.methods[method]
            logging.info(self._setup_defaults_(db, c, identity))
            return method(db, c, table, data)
        elif self.groupme:
            db, c = self.connect(groupme_data)
            method = self.methods[method]
            logging.info(self._setup_defaults_(db, c, identity))
            return method(db, c, table, data)
        else:
            return print("You never defined a client!")


if __name__ == "__main__":
    testingDiscord = QuizBotDataHandler(discord=True)
    testingGroupMe = QuizBotDataHandler(groupme=True)
    testingErrors = QuizBotDataHandler()

    test_data = {
        "name" : "tester",
        "groupid" : 132,
        "table" : ["config", "allownsfw"],
        "data" : ["true","tester", 132]
    }
    print(test_data["data"])
    print(testingDiscord.do("update", test_data))
    print(testingGroupMe.do("update", test_data))
    print(testingErrors.do("update", test_data))
