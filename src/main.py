from time import time
import json
import praw
import os
from dotenv import load_dotenv
import re
import random
import traceback

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
SECRET_KEY = os.getenv('SECRET_KEY')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

reddit = praw.Reddit(
    client_id = CLIENT_ID,
    client_secret = SECRET_KEY,
    username = USERNAME,
    password = PASSWORD,
    user_agent = 'nallaBot'
)

auth_user = reddit.user.me()

responseFile = open("responses.json", "r")
responses = json.load(responseFile)
custom_reply_users = list(responses["custom"])

class Analyse:
    def __init__(self, comment: praw.reddit.Comment):
        self.comment = comment
        self.caller = comment.author
        self.target = self.setTarget()
        self.timeLimit = self.setTimeLimit()
        self.stats = self.getStats()
        self.judgement = self.getJudgement()

    def setTarget(self):
        is_reply = not comment.parent().id.startswith('t3_')
        body = self.comment.body.lower().replace('\n','').strip()
        wordList = body.split()
        target = ''
        if 'botstats' in wordList:
            target = auth_user
        elif 'me' in wordList or 'self' in wordList:
            target = comment.author
        elif 'op' in wordList:
            target = comment.submission.author
        else:
            mentions = []
            for word in wordList:
                if word.startswith('u/') and len(word)>=4 and word.replace('u/','') != auth_user.name.lower():
                    word = word.replace('u/','')
                    mentions.append(word)
            if len(mentions) != 0:
                target = reddit.redditor(mentions[0])
            else:
                if is_reply:
                    parent_author = comment.parent().author
                    if parent_author.id == auth_user.id:
                        target = comment.author
                    else:
                        target = parent_author
                else:
                    target = comment.author

        return target

    def setTimeLimit(self):
        wordList = re.sub(r'[^\w\s]','',self.comment.body).strip()
        factor = 7
        if 'day' in wordList or 'days' in wordList:
            factor = 1
        elif 'week' in wordList or 'weeks' in wordList:
            factor = 7
        elif 'month' in wordList or 'months' in wordList:
            factor = 30
        elif 'year' in wordList or 'years' in wordList:
            factor = 365

        j = 1
        for word in wordList:
            if word.isdigit():
                j = int(word)
                break
        limit = j*factor

        return limit

    def getStats(self):
        limit_utc = int(time()) - self.timeLimit*60*60*24
        last_comment_utc = 0

        total_comments = int(0)
        total_votes = int(0)

        user_comments = self.target.comments.new(limit=None)
        for comment in user_comments:
            if comment.created_utc <= limit_utc:
                break
            total_comments += 1
            total_votes += comment.score

            last_comment_utc = int(comment.created_utc)

        total_comments = str(total_comments)
        total_votes = str(total_votes)

        days = self.timeLimit

        reachedLimit = False
        if int(total_comments) >= 975:
            reachedLimit = True
            days = int((time() - last_comment_utc)/86400)
            total_comments += "+"
            total_votes += "+"

        comments_per_day = str(round(int(total_comments.replace("+",""))/days,2))
        if reachedLimit:
            comments_per_day += "+"

        intro = "Oh so you wanna see my stats? Here you go!"
        if not self.target.name.lower() == auth_user.name:
            if self.target.name.lower() == self.caller.name.lower():
                intro = f"Beep Boop! nallaBot here to judge you!\n\nHere are your comment stats from last {self.timeLimit} days:"
            else:
                intro = f"Beep Boop! nallaBot here to judge u/{self.target.name}!\n\nHere's their comment stats from last {self.timeLimit} days:"

        stat_str = f'''
{intro}

```
Total comments: {total_comments}
Total votes: {total_votes}
Comments per day: {comments_per_day}
```
'''

        self.comments_per_day = float(comments_per_day.replace("+",""))

        return stat_str

    def getJudgement(self):
        if self.target.name.lower() == auth_user.name.lower():
            return ""

        cpd = int(round(self.comments_per_day))
        target_name = self.target.name.lower()
        if target_name not in custom_reply_users:
            key = ""
            if cpd <= 3:
                key = "min"
            elif cpd <= 8:
                key = "low"
            elif cpd <= 15:
                key = "mid"
            elif cpd <= 25:
                key = "high"
            elif cpd <= 130:
                key = "extreme"
            else:
                key = "max"
            response = random.choice(responses["standard"][key]).replace("$cpd", str(self.comments_per_day))
        else:
            response = random.choice(responses["custom"][target_name])

        judgementText = f'''
Here's what I think about you based on the above stats:

>!{response}!<\n
'''

        return judgementText

while True:
    inbox = reddit.inbox.unread(limit=None)
    for comment in inbox:
        try:
            body = comment.body.lower()

            if not auth_user.name.lower() in body:
                continue

            mentions_count = 1
            mentions_limit = 100
            mention_utc = 0
            for c in comment.author.comments.new(limit=None):
                if c.created_utc < int(time()) - 3600:
                    break
                if auth_user.name.lower() in c.body.lower():
                    mention_utc = int(comment.created_utc)
                    mentions_count+=1
            if mentions_count > mentions_limit:
                reply = f"You have already called the bot {mentions_count} times in last 1 hour, try again in {int((mention_utc+3600-int(time()))/60)} minutes"
                print(reply)
                comment.mark_read()
                continue

            analysis = Analyse(comment)

            links = f"^([github](https://github.com/fahadreyaz/nallaBot) | [how to use](https://reddit.com))"
            reply = analysis.stats + analysis.judgement + links
            comment.reply(body=reply)

            comment.mark_read()
            print(f"replied to u/{analysis.caller}")

        except Exception:
            comment.mark_read()
            print(f"Error in processing comment: reddit.com{comment.context}")
            print(traceback.format_exc())
            continue
