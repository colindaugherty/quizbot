# database handler for quizbot

import sqlite3, logging, traceback

datalogger = logging.getLogger(__name__)

datalogger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('logs/data.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('QuizBot[DATA]: %(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the file handler to the logger
datalogger.addHandler(handler)

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
        c.execute("""CREATE TABLE IF NOT EXISTS players
        (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, groupid int, users text, wins int, questions int, lifetimeWins int, lifetimeQuestions int, lifetimeRewards int)
        """)

        c.execute("SELECT * FROM config WHERE name=? AND groupid=?", identity)
        checkconfig = c.fetchone()
        c.execute("SELECT * FROM memesource WHERE name=? AND groupid=?", identity)
        checkmemesource = c.fetchone()
        c.execute("SELECT * FROM stats WHERE name=? AND groupid=?", identity)
        checkstats = c.fetchone()
        if checkconfig == None and checkmemesource == None or None in checkconfig and None in checkmemesource:
            datalogger.info(f"Doing default config for bot {name} in group {groupid}")
            insertvalues = [(name, groupid, 'false','false')]
            c.executemany("INSERT INTO config (name, groupid, allownsfw, allowrepost) VALUES (?,?,?,?)", insertvalues)
            insertvalues = [(name, groupid, 'all')]
            c.executemany("INSERT INTO memesource (name, groupid, subreddit) VALUES (?,?,?)", insertvalues)
            datalogger.info("Finished - results:\n")
            for row in c.execute("SELECT * FROM config ORDER BY id"):
                datalogger.info(row)
            for row in c.execute("SELECT * FROM memesource ORDER BY groupid"):
                datalogger.info(row)
            db.commit()
        else:
            for row in c.execute("SELECT * FROM config ORDER BY id"):
                datalogger.info(row)
            for row in c.execute("SELECT * FROM memesource ORDER BY groupid"):
                datalogger.info(row)
        datalogger.info("-- DOING STATS --")
        if checkstats == None or None in checkstats:
            datalogger.info(f"Setting up stats for bot {name} in group {groupid}")
            insertvalues = [(name, groupid, 0, 0, 0, 0)]
            c.executemany("INSERT INTO stats (name, groupid, requests, responses, FredResponses, TotalMessages) VALUES (?, ?, ?, ?, ?, ?)", insertvalues)
            for row in c.execute("SELECT * FROM stats ORDER BY groupid"):
                datalogger.info(row)
            db.commit()
        else:
            for row in c.execute("SELECT * FROM stats ORDER BY groupid"):
                datalogger.info(row)

        datalogger.info("Finished setting defaults")
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
            datalogger.info(f"Editing database with this data- {data}")
            datalogger.info(f"Table is {table} and subtable is {table[1]}")
            datalogger.info(f"Table is a list: {isinstance(table, list)}")
            datalogger.info(f"Type of table: {type(table)}")
            if table == "opt":
                c.executemany("UPDATE opt SET newsroom=? AND elimination=? WHERE (name=? AND groupid=?)", [data])
                db.commit()
                self.clean_up(db, c)
                return True
            elif isinstance(table, list):
                subtable = table[1]
                datalogger.info(f"Table is {table} and subtable is {subtable}")
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
                elif table[0] == "opt":
                    if subtable == "newsroom":
                        c.executemany("UPDATE opt set newsroom = ? WHERE (name=? AND groupid=? AND users=?)", [data])
                        db.commit()
                        self.clean_up(db, c)
                        return True
                    elif subtable == "elimination":
                        c.executemany("UPDATE opt set elimination = ? WHERE (name=? AND groupid=? AND users=?)", [data])
                        db.commit()
                        self.clean_up(db, c)
                        return True
                    else:
                        return f"Couldn't find subtable {subtable} in table {table[0]}"
                elif table[0] == "players":
                    if subtable == "wins":
                        datalogger.info(f"\n\nupdating wins with this data {data}\n\n")
                        c.executemany("UPDATE players set wins = wins + 1 WHERE (name=? AND groupid=? AND users=?)", [data])
                        c.executemany("UPDATE players set lifetimeWins = lifetimeWins + 1 WHERE (name=? AND groupid=? AND users=?)", [data])
                        db.commit()
                        self.clean_up(db, c)
                        return True
                    elif subtable == "questions":
                        c.executemany("UPDATE players set questions = questions + 1 WHERE (name=? AND groupid=? AND users=?)", [data])
                        c.executemany("UPDATE players set lifetimeQuestions = lifetimeQuestions + 1 WHERE (name=? AND groupid=? AND users=?)", [data])
                        db.commit()
                        self.clean_up(db, c)
                        return True
                    elif subtable == "lifetimeRewards":
                        c.executemany("UPDATE players set lifetimeRewards = lifetimeRewards + 1 WHERE (name=? AND groupid=? AND users=?)", [data])
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
            datalogger.info("Finished editing database.")
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
            elif table == "players":
                c.executemany("INSERT INTO players (name, groupid, users, wins, questions, lifetimeWins, lifetimeQuestions, lifetimeRewards) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", [data])
                db.commit()
                self.clean_up(db, c)
                return True
            else:
                return f"This should really only be used for adding memesource, authenticated/new opt users, or updating score stats of players, however, it was used for {table}"
        except Exception as e:
            self.clean_up(db, c)
            print(traceback.format_exc())
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
                db.commit()
                self.clean_up(db, c)
                return True
            elif table == "players":
                c.executemany("UPDATE players set wins = 0 WHERE (name=? AND groupid=?)", [data])
                c.executemany("UPDATE players set questions = 0 WHERE (name=? AND groupid=?)", [data])
                db.commit()
                self.clean_up(db, c)
                return True
            else:
                return f"This should really only be used for deleting memesource and authenticated users, it was used for {table}"
        except Exception as e:
            self.clean_up(db, c)
            print(traceback.format_exc())
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
                    return f"Table {table} is not supported for lists.\ncompatible tables are: config, stats"
            elif table == "memesource":
                c.execute("SELECT subreddit FROM memesource WHERE (name=? AND groupid=?)", data)
                data = c.fetchone()
                return data[0]
            elif table == "authenticate":
                c.execute("SELECT users FROM authenticate WHERE (name=? AND groupid=?)", data)
                data = c.fetchone()
                if data == None or None in data or data == []:
                    return None
                else:
                    return data[0]
            elif table == "opt":
                c.execute("SELECT users FROM opt WHERE (name=? AND groupid=?)", data)
                data = c.fetchone()
                if data == None or None in data or data == []:
                    return None
                else:
                    return data[0]
            elif table == "players":
                c.execute("SELECT users FROM players WHERE (name=? AND groupid=? AND users=?)", data)
                data = c.fetchone()
                datalogger.info(f"\n\nData for the player score lookup is - {data}\n\n")
                if data == None or None in data or data == []:
                    return None
                else:
                    return data[0]
        except Exception as e:
            self.clean_up(db, c)
            print(traceback.format_exc())
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
                    return f"Table {table} is not supported for lists.\ncompatible tables are: config, stats"
            elif table == "memesource":
                data = [subreddit[0] for subreddit in c.execute("SELECT subreddit FROM memesource WHERE (name=? AND groupid=?)", data)]
                if data == None or None in data or data == []:
                    return None
                else:
                    return data
            elif table == "authenticate":
                data = [user[0] for user in c.execute("SELECT users FROM authenticate WHERE (name=? AND groupid=?)", data)]
                if data == None or None in data or data == []:
                    return None
                else:
                    return data
            elif table == "opt":
                data = [user[0] for user in c.execute("SELECT users FROM opt WHERE (name=? AND groupid=?)", data)]
                if data == None or None in data or data == []:
                    return None
                else:
                    return data
            elif table == "players":
                data = [user[0] for user in c.execute("SELECT * FROM players WHERE (name=? AND groupid=?)", data)]
                if data == None or None in data or data == []:
                    return None
                else:
                    return data
        except Exception as e:
            self.clean_up(db, c)
            print(traceback.format_exc())
            return f"Encountered error - {e}"

    def do(self, method, data):
        identity = (str(data["name"]), int(data["groupid"]))
        table = data["table"]
        data = tuple(data["data"])
        datalogger.info(f"Identity: {identity}\nTable: {table}\nData: {data}")
        if self.discord:
            db, c = self.connect(discord_data)
            method = self.methods[method]
            datalogger.info(self._setup_defaults_(db, c, identity))
            return method(db, c, table, data)
        elif self.groupme:
            db, c = self.connect(groupme_data)
            method = self.methods[method]
            datalogger.info(self._setup_defaults_(db, c, identity))
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
        "table" : "authenticate",
        "data" : ["tester", 132]
    }
    print(test_data["data"])
    print(testingDiscord.do("selectone", test_data))
    print(testingGroupMe.do("select", test_data))
    # print(testingErrors.do("update", test_data))
