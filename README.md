# nallaBot

`nallaBot` is a Reddit bot written in Python using [PRAW(Python Reddit API Wrapper)](https://praw.readthedocs.io/en/latest/). It is a bot that can be ued to display the comment statistics of a user.

## Table of Contents
1. [Introduction](#introduction)
2. [Libraries Used](#libraries-used)
3. [Usage](#usage)
    1. [Keywords](#keywords)
    2. [Setting time limit to analyse comments](#setting-time-limit-to-analyse-comments)
    3. [Example](#example)
4. [Contributing](#contributing)

---

## Introduction
The word _**nalla**_ is often used to refer to a person who is useless or incompetent. It is considered to be a derogatory term. `nallaBot` is a simple Reddit bot written in Python using PRAW. It displays the comment statistics of a user and also uses OpenAI's `gpt-3.5-turbo` model to generate a sarcastic comment based on user's comment history.

---

## Libraries Used
- [Python](https://www.python.org/)
- [PRAW](https://praw.readthedocs.io/en/latest/) is used to interact with Reddit's API. It can be installed using `pip install praw`.
- [OpenAI](https://openai.com/) is used to generate a sarcastic comment based on user's comment history. It can be installed using `pip install openai`.
- [python-dotenv](https://pypi.org/project/python-dotenv/) is used to load environment variables from a `.env` file. It can be installed using `pip install python-dotenv`.

---

## Usage
Mention the bot in the [comments here](https://www.reddit.com/user/nallaBot/comments/133nl5n/) to check your comment statistics.

- `u/nallabot` : shows the stats of comment author if mention is a top level comment and shows the stats of the author of the reply of comment mentioning the bot if mention is a reply to another comment.

- `u/nallabot` u/username : shows statistics for user u/username.
---
### Keywords
`op` : shows statistics for author of the post the comment belongs to.

`self` or `me` : shows statistics for comment author.

`botstats` : shows statistics for the bot itself.

---
### Setting time limit to analyse comments
By default it it set to 7 days, however you can change this by typing the duration in the bot mentioned in form of days, weeks, months or years

Examples:

- `u/nallabot self 100 days`

- `u/nallabot u/abc 2 weeks`

- `u/nallabot 1 year`

> Note: Reddit API only allows to fetch upto about 1000 recent comments of a user, so no matter what you set the time limit to, the bot will show stats with only last 1000 comments.

---
### Example

    Beep Boop! nallaBot here to judge you!

    Here are your comment stats from last 7 days:

    Total comments: 66
    Total votes: 226
    Comments per day: 9.43

    Here's what I think about you based on the above stats:

    Ah so you're one of those people who don't like to comment much often

    github | how to use

You can visit [this link](https://www.reddit.com/user/nallaBot/comments/133nl5n/) to see more examples.

---
## Contributing
Feel free to contribute to this project by opening an issue or creating a pull request.

