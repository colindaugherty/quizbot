# fun sayings from quizbot

import random
from datetime import datetime

class QuizBotFunSayings:
    def __init__(self, sender_name):
        
        fun_sayings = [
            "Why was I created? I don't know. It's something I ask myself daily. - Fred",
            "Oh, shut up Weatherby - Fred",
            "I think we've outgrown full time education - Fred",
            "Vanessa named me, so I guess I'm Fred now.",
            "a dancing man? i think yes - \n  o /\n/ |  \n/  \\",
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
            "Yeah, but did you get an amazing lanyard of winning? Nope.",
            "i :handshake: was :relieved: a :man_fairy_tone1: girl :girl_tone1: in :hugging: the :smile: village :house_with_garden: doing :grinning: all :woman_gesturing_ok_tone1: right :woman_tipping_hand_tone1: then :sparkles: i became :butterfly: a princess :princess: overnight :new_moon_with_face: now i gotta :man_fairy_tone1: figure :nerd:out :raised_hands_tone1: how to do :handshake: it right :thumbsup_tone1: so much :scream_cat: to learn :books: and see :eye::lips::eye: up :point_up_2_tone1: in the castle :european_castle: with my new family :family_mwgb: in a school :school: that just :relieved: for royalty :crown: a whole :hole: enchanted :woman_fairy_tone1: world :earth_africa: is waiting :raised_hand_tone1: for me :woman_tipping_hand_tone1: im so :dizzy: excited to :star_struck: be sOFIA THE FIRST :pleading_face::moyai::pensive::punch::star_struck::heartpulse::star_struck::kissing::dizzy::school::purple_heart::strawberry::sob::v::birthday: i’m finding :mag: out what :flushed: being royal's :princess_tone1: all about :star_struck: (sofia the first :kissing_smiling_eyes:) makin my :sunglasses: way its :rainbow: an adventure :woman_climbing: everyday :woman_gesturing_ok_tone1: SOFIA :dizzy: it’s gonna :stuck_out_tongue:be :face_with_hand_over_mouth: my time :alarm_clock: SOFIA :woman_fairy_tone1: to show :tickets: them all :sunglasses: that im :relieved: sofia the fiiIIiIiIiirsTtTtT :kissing::point_up:",
            "I cut my finger on my moms wring\nI hope I can still dance",
            "*dab on them haters*\nヽ( •_)ᕗ",
            "what do you call a chicken farmer?\n.\n.\n.\nA CHICKEN TENDER",
            # f"Read {datetime.now.time.hour}:{datetime.now.time.minute}",
            "If you wear cowboy clothes, are you ranch dressing?",
            "Please not now, I'm introverting",
            "Bible Bowlers are easily confused",
            "I can't brain today, I have the dumb",
            "In my defense- I was left unsupervised",
            "surely not everyone was kung fu fighting.....",
            "I'd love to stay and chat, but I'm lying",
            "*default dances on the haterz*",
            "If Ben and Megan started a fan club, it'd be a khul club -Samuel"
            ]

        rand = random.randint(0, len(fun_sayings) - 1)
        message = fun_sayings[rand]
        message += "\n(this message was summoned by {})".format(sender_name)

        self.response = message