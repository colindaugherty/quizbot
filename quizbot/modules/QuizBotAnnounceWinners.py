

class QuizBotAnnounceWinners:
    def __init__(self, botname, groupid, handler):
        data = {"name" : botname, "groupid" : groupid, "table" : "players", "data" : [botname, groupid]}
        winners = handler.do("selectall", data)
        winners = sorted(winners, key = lambda x: int(x[4]), reverse=True)
        response = "Here are your winners for this week!\nStarting with wins we have:\n"

        for winner in winners[0:3]:
            response += f"{winner[3]} with {winner[4]} wins\n"
        
        winners = sorted(winners, key = lambda x: int(x[4]), reverse=True)
        response += "Your winners for total questions answered correctly are:\n"
        
        for winner in winners[0:3]:
            response += f"{winner[3]} with {winner[5]} questions answered\n"

        response += "Thanks for playing quizbot, and play more to get a chance to be featured here!\n"
        data = {"name" : botname, "groupid" : groupid, "table" : "players", "data" : [botname, groupid]}
        confirmDelete = handler.do("delete", data)
        if confirmDelete == True:
            self.response = response
        else:
            self.response = f"Had an error in trying to reset scores. Here you go {confirmDelete}"