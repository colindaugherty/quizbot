# class to send meme from reddit

import praw, time, random, logging

reddit = praw.Reddit(client_id="pPp18DiGR-UnFA", client_secret="vmY57gKz-6l01ePkoC2FMmv1nv4", user_agent="groupmebot /u/b1ackzi0n")

class QuizBotSendRedditMeme:
    def __init__(self, memesource, source_len):
        start = time.time()
        meme_message = "Meme response-\n'"
        rand = random.randint(0, source_len)
        subreddit = memesource[rand]
        logging.info(subreddit)
        submission_list = []
        for submission in reddit.subreddit(subreddit).hot(limit=10):
            if submission.stickied != True:
                submission_list.append(submission)
            else:
                logging.info("We don't approve of stickied messages")
        submission_list_length = len(submission_list) - 1
        rand = random.randint(0,submission_list_length)
        logging.info("Got a random submission index of %d out of %d\nIt has an upvote ratio of %d" % (rand, submission_list_length, submission_list[rand].upvote_ratio))
        logging.info("Printing url link for post '%s'-\n" % (submission_list[rand].title))
        if submission_list[rand].selftext == "":
            logging.info(submission_list[rand].url)
            result = submission_list[rand].url
        else:
            logging.info(submission_list[rand].shortlink)
            result = submission_list[rand].shortlink
        meme_message += submission_list[rand].title
        meme_message += "' from the subreddit '"
        meme_message += submission_list[rand].subreddit.display_name
        meme_message += "'\n"
        meme_message += result
        meme_message += "\nI hope you enjoy!\n"
        meme_message += "response_time: "
        response_time = time.time() - start
        if time.strftime("%S", time.gmtime(response_time)) == "00":
            meme_message += "< 0s"
        else:
            meme_message += time.strftime("%Ss", time.gmtime(response_time))

        self.response = meme_message