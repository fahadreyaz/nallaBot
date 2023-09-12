import time
import json
import praw
import os
from dotenv import load_dotenv
import re
import traceback

from prawcore import RequestException

from api import OpenAi

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
SECRET_KEY = os.getenv('SECRET_KEY')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=SECRET_KEY,
    username=USERNAME,
    password=PASSWORD,
    user_agent='nallaBot'
)

auth_user = reddit.user.me()

infoFile = open("info.json", "r")
info = json.load(infoFile)
custom_users = list(info["custom"])


class Analyse:
    def __init__(self, comment: praw.reddit.Comment):
        self.comment = comment
        self.caller = comment.author
        self.target = self.setTarget()
        self.timeLimit = self.setTimeLimit()
        self.stats = self.getStats()
        self.judgement = self.getJudgement()

    def setTarget(self):
        is_reply = not comment.parent_id.startswith('t3_')
        body = self.comment.body.lower().replace('\n', '').strip()
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
                if word.startswith('u/') and len(word) >= 4 and word.replace('u/', '') != auth_user.name.lower():
                    word = word.replace('u/', '')
                    mentions.append(word)
            if len(mentions) != 0:
                target = reddit.redditor(mentions[0])
            else:
                if is_reply:
                    parent_author = reddit.redditor(comment.parent().author)
                    if parent_author.id == auth_user.id:
                        target = comment.author
                    else:
                        target = parent_author
                else:
                    target = comment.author

        return target

    def setTimeLimit(self):
        wordList = re.findall(r'\d+|\D+', self.comment.body)
        factor = 7
        for i in range(len(wordList)):
            if wordList[i].isdigit() and i < len(wordList)-1:
                unit = wordList[i+1].lower()
                if 'day' in unit or 'days' in unit:
                    factor = 1
                    break
                elif 'week' in unit or 'weeks' in unit:
                    factor = 7
                    break
                elif 'month' in unit or 'months' in unit:
                    factor = 30
                    break
                elif 'year' in unit or 'years' in unit:
                    factor = 365
                    break

        j = 1
        for word in wordList:
            if word.isdigit():
                j = int(word)
                break
        limit = j*factor

        return limit

    def getStats(self):
        limit_utc = int(time.time()) - self.timeLimit*60*60*24
        last_comment_utc = 0

        total_comments = int(0)
        total_votes = int(0)

        subsList = []

        user_comments = self.target.comments.new(limit=None)
        for comment in user_comments:
            if comment.created_utc <= limit_utc:
                break
            subsList.append(comment.subreddit.display_name)
            total_comments += 1
            total_votes += comment.score

            last_comment_utc = int(comment.created_utc)

        subsDict = {}
        for sub in subsList:
            if sub in subsDict:
                subsDict[sub] += 1
            else:
                subsDict[sub] = 1

        listStr = ""
        for sub in subsDict.keys():
            listStr += f"\nr/{sub}: {subsDict[sub]}\n"

        listStr = listStr[1:-1]
        self.subsList = listStr

        total_comments = str(total_comments)
        total_votes = str(total_votes)

        days = self.timeLimit

        reachedLimit = False
        if int(total_comments) >= 975:
            reachedLimit = True
            days = int((time.time() - last_comment_utc)/86400)
            total_comments += "+"
            total_votes += "+"

        comments_per_day = str(
            round(int(total_comments.replace("+", ""))/days, 1))
        if reachedLimit:
            comments_per_day += "+"

        intro = f"Oh so you wanna see my stats from last {self.timeLimit} days? Here you go!"
        if not self.target.name.lower() == auth_user.name.lower():
            if self.target.name.lower() == self.caller.name.lower():
                intro = f"Beep Boop! nallaBot here to judge you!\n\nHere are your comment stats from last {self.timeLimit} days:"
            else:
                intro = f"Beep Boop! nallaBot here to judge u/{self.target.name}!\n\nHere's your comment stats from last {self.timeLimit} days:"

        stat_str = f'''
{intro}

```
Total comments: {total_comments}
Total votes: {total_votes}
Comments per day: {comments_per_day}
```

Here's a detailed list of your comments activity:
```
{listStr}
```

'''

        self.comments_per_day = int(float(comments_per_day.replace("+","")))
        self.total_comments = int(float(total_comments.replace("+","")))
        self.total_votes = int(total_votes)

        return stat_str

    def getJudgement(self):
        if self.target.name.lower() == auth_user.name.lower():
            return ""

        target = self.target

        comments_count = self.total_comments
        cpd = self.comments_per_day
        votes = self.total_votes
        time_limit = self.timeLimit

        extraInfo = []

        subsList = self.subsList.replace("\n",",").replace(",,",", ")

        if target.name.lower() in custom_users:
            extraInfo = info["custom"][target.name.lower()]


        if cpd <= 15:
            prompt = f"My reddit username is {target}, I have posted {comments_count} comments on reddit in last {time_limit} days and got a total of {votes} votes on them. I have posted {cpd} comments per day on reddit on average. Here is a detailed list of subreddits I have been active in with number of comments i have made in them: [{subsList}]. Here is a list of some extra info about me: {str(extraInfo)}. Respond in a snarky way appreciating me for my low reddit usage in under 20-25 words"
        elif cpd <=30:
            prompt = f"My reddit username is {target}, I have posted {comments_count} comments on reddit in last {time_limit} days and got a total of {votes} votes on them. I have posted {cpd} comments per day on reddit on average. Here is a detailed list of subreddits I have been active in with number of comments i have made in them: [{subsList}]. Here is a list of some extra info about me: {str(extraInfo)}. Respond in a snarky way brutally roasting me for my high reddit usage in under 40-50 words"
        else:
            prompt = f"My reddit username is {target}, I have posted {comments_count} comments on reddit in last {time_limit} days and got a total of {votes} votes on them. I have posted {cpd} comments per day on reddit on average. Here is a detailed list of subreddits I have been active in with number of comments i have made in them: [{subsList}]. Here is a list of some extra info about me: {str(extraInfo)}. Respond in a snarky way brutally roasting me for my extremely high reddit usage in under 60-80 words [use 50% swearing]"

        response = OpenAi(prompt=prompt).getResponse()

        judgementText = f'''
Here's a message for you based on the above stats:

>!{response}!<
        '''

        return judgementText
print("Bot running...")
while True:
    time.sleep(2)
    inbox = reddit.inbox.unread(limit=None)
    for comment in inbox:
        try:
            body = comment.body.lower()

            if not auth_user.name.lower() in body:
                continue

            mentions_count = 1
            mentions_limit = 3
            mention_utc = 0
            for c in comment.author.comments.new(limit=None):
                if c.created_utc < int(time.time()) - 3600:
                    break
                if auth_user.name.lower() in c.body.lower():
                    mention_utc = int(comment.created_utc)
                    mentions_count += 1
            if mentions_count > mentions_limit:
                reply = f"You have already called the bot {mentions_count} times in last 1 hour, try again in {int((mention_utc+3600-int(time.time()))/60)} minutes"
                comment.reply(body=reply)
                comment.mark_read()
                continue

            analysis = Analyse(comment)

            links = f"\n\n^([github](https://github.com/fahadreyaz/nallaBot) | [how to use](https://www.reddit.com/user/nallaBot/comments/133nl5n))"
            reply = analysis.stats + analysis.judgement + links
            comment.reply(body=reply)

            comment.mark_read()
            print(f"replied to u/{analysis.caller}")

            time.sleep(1)

        except Exception as e:
            if e is RequestException:
                pass
            comment.mark_read()
            print(f"Error in processing comment: reddit.com{comment.context}")
            print(traceback.format_exc())
            continue
