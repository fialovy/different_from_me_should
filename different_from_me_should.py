import re
from pathlib import Path

import praw


# i will make this modular later :P
def different_from_me_should():
    # Note that this uses a praw.ini in a separate config directory ($HOME/.config
    # for me on Linux). That is where the dfm_bot argument comes from, as
    # well as the user_agent and authentication creds.
    # See https://praw.readthedocs.io/en/stable/getting_started/configuration/prawini.html
    subreddit_lists_path = Path("subreddit_lists")
    subreddits_by_subject = {}

    for subreddit_list_file in subreddit_lists_path.iterdir():
        subreddit_match = re.match(r"(.*)_subreddits.txt", subreddit_list_file.name)
        subreddit_subject = subreddit_match.group(1)
        with open(subreddit_lists_path / subreddit_list_file.name, "r") as listfile:
            subreddits = {subname.strip() for subname in listfile.readlines()}
            subreddits_by_subject[subreddit_subject] = subreddits

    # literally just see if we can access this first
    reddit = praw.Reddit("dfm_bot")
    for subject, subs in subreddits_by_subject.items():
        print(f"***** SUBJECT: {subject}")
        for sub in subs:
            sub_reader = reddit.subreddit(sub)
            for submission in sub_reader.hot(limit=5):
                print(submission.title)


if __name__ == "__main__":
    different_from_me_should()
