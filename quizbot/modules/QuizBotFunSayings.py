# fun sayings from quizbot

import random

class QuizBotFunSayings:
    def __init__(self, sender_name):
        
        fun_sayings = [
            "Why was I created? I don't know. It's something I ask myself daily. - Fred",
            "Oh, shut up Weatherby - Fred",
            "I think we've outgrown full time education - Fred",
            "Vanessa named me, so I guess I'm Fred now.",
            "  o /\n/ |  \n / \ \nlook it's a guy dancing! - Fred",
            "uh, i don't know what to say anymore. uh. good morning? or is it afternoon now? evening? - Fred",
            "I may be the biggest news to hit Bible Bowl since The Great Gulon Incident three years ago - WHICH, by the way, I had nothing to do with.",
            "Smile, Patrick (or Nick depending on which Bible Bowl generation you're from.)",
            "IS THIS A KISSING BOOK?", "In Memoriam - Mr. Bacon. Thanks for the breakfast.",
            "shoot me in the face and steal my gun",
            "Ask me no questions, I will tell you no lies.",
            "All hail Chairman Mao",
            "And help us to remember, it's not about winning or losing, but about learning Your Word. Amen.",
            "Shhhhhh, no one cares",
            "I'm totes yeet yo!",
            "I wrote the rules John.",
            "A day without sunshine, is like. You know. Night.",
            "Remember if you can't say something nice, make it funny.",
            "Sometimes I'm funny, sometimes I'm quiet, sometimes I'm ecstatic, but I am always Fred",
            "If you see someone crying ask if it's because of their haircut.",
            "Bro. When you clean out a vacuum cleaner. You become. The vacuum cleaner.",
            "We get more starlight during the day than we do at night.",
            "Onions basically force you to mourn their death. How does that make you feel? You monster.",
            "Umm, I contest, there's an unbearable bot in the chat.",
            "Bible Bowl is like playing chess. Except the chess board is a buzzer board. And you talk a lot more. And there's nothing in it like chess. Except time. We keep time.",
            "Sorry, Samuel & Vanessa, I'm not authenticating you - Fred",
            "He used to have red hair and is clinging to his childhood. - Sarah",
            "I vote for equality, so y'all can shoot each other if you want but lol I NEEEED SMORES - Chris",
            "Yeah, but did you get an amazing lanyard of winning? Nope."
            ]

        rand = random.randint(0, len(fun_sayings) - 1)
        message = fun_sayings[rand]
        message += "\n(this message was summoned by {})".format(sender_name)

        self.response = message