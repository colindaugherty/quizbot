import random

class QuizBotFortuneCookie:
    def __init__(self, sender):

        self.initial = [
            sender,
            f"{sender}'s aunt",
            f"{sender}'s dog",
            "A singular buzzer board",
            "The brain of the doctor of Frankenstein",
            "Doge",
            "Fred",
            "Pizza",
            "ur mom",
            "The house",
            "An absolute lad",
            f"{sender}'s most prized possession",
            "Sophia the first",
            "A painting",
            "A fortune cookie",
            "A message from the King of England",
            "The youth",
            sender,
            f"{sender}"
        ]

        self.finale = [
            "ran away from home. Be on the lookout.",
            "is running. Don't ask where",
            "said to me once, \"You know what? Just don't\"",
            "approves",
            "thinks the world of you :love_you_gesture:",
            "once sat me down and said, \"You know how you ask a lot of questions? Stop it\"",
            "really wants you to go to bed",
            "- Happy you will be.",
            "will soon enter into your house with a present. Do not question it.",
            "thinks you should stop pushing their buttons so much",
            "really just wants you to settle down so they can do what they came to do.",
            "wants you to know. JUST EAT THE VEGGIES THEY ARENT THAT BAD",
            "said a wise man once said, \"You should always learn from your mistakes. You will learn a lot today\"",
            "wants you to know - standing on one's head at job interviews forms a lasting impression.",
            "thinks that a kangaroo is really just a rabbit on steroids.",
            "wonders if it could be called a beach if there was no sand.",
            "gets their lunch money from the local wishing well.",
            "says, \"no u\""
        ]

        self.response = f"{random.choice(self.initial)} {random.choice(self.finale)}\na fortune cookie opened by {sender}"