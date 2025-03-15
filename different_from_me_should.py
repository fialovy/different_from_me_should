import re
from pathlib import Path

import markovify
import praw

import nltk
from nltk.tokenize import sent_tokenize

POST_LIMIT_PER_SUB = 500
# Per markovify docs (https://pypi.org/project/markovify/#basic-usage), state
# size is "a number of words the probability of a next word depends on"
OTHER_PEOPLE_SHOULD = "Other people should"
STATE_SIZE = len(OTHER_PEOPLE_SHOULD.split(" "))
FORCED_SEEDS = {
    f"{OTHER_PEOPLE_SHOULD} do this.",
    f"{OTHER_PEOPLE_SHOULD} be kinder.",
    f"{OTHER_PEOPLE_SHOULD} understand this.",
    f"{OTHER_PEOPLE_SHOULD} work toward this.",
    f"{OTHER_PEOPLE_SHOULD} notice this.",
    f"{OTHER_PEOPLE_SHOULD} try this.",
    f"{OTHER_PEOPLE_SHOULD} do better.",
    f"{OTHER_PEOPLE_SHOULD} get involved.",
    f"{OTHER_PEOPLE_SHOULD} be more aware of this.",
    f"{OTHER_PEOPLE_SHOULD} care about this.",
    f"{OTHER_PEOPLE_SHOULD} just stop.",
    f"{OTHER_PEOPLE_SHOULD} stop trying to do this.",
    f"{OTHER_PEOPLE_SHOULD} stop doing this.",
    f"{OTHER_PEOPLE_SHOULD} not have to worry about this.",
    f"{OTHER_PEOPLE_SHOULD} decide for themselves.",
    f"{OTHER_PEOPLE_SHOULD} figure out the best way to make this work.",
}
SENTENCE_GENERATION_ATTEMPTS = 1000

# prerequisite
nltk.download('punkt_tab')

# i will make this modular later :P
def different_from_me_should():
    # Note that this uses a praw.ini in a separate config directory ($HOME/.config
    # for me on Linux). That is where the dfm_bot argument comes from, as
    # well as the user_agent and authentication creds.
    # See https://praw.readthedocs.io/en/stable/getting_started/configuration/prawini.html
    subreddit_lists_path = Path("subreddit_lists")
    corpuses_by_subreddit_by_subject = {}

    for subreddit_list_file in subreddit_lists_path.iterdir():
        subreddit_match = re.match(r"(.*)_subreddits.txt", subreddit_list_file.name)
        subreddit_subject = subreddit_match.group(1)
        with open(subreddit_lists_path / subreddit_list_file.name, "r") as listfile:
            subreddits = {subname.strip() for subname in listfile.readlines()}
            corpuses_by_subreddit_by_subject[subreddit_subject] = {
                subreddit: "" for subreddit in subreddits
            }

    # Populate a corpus based on this year's top posts and/or comments
    reddit = praw.Reddit("dfm_bot")
    for subject, corpuses_by_subreddit in corpuses_by_subreddit_by_subject.items():
        print(f"***** SUBJECT: {subject}")
        for sub in corpuses_by_subreddit:
            # Seed the sub corpus with a huge number of 'arbitrary' sentences that
            # start with my desired prefix, since I am unlikely to find it in
            # the wild.
            for seed_sentence in FORCED_SEEDS:
                corpuses_by_subreddit_by_subject[subject][sub] += f'{seed_sentence} '

            sub_reader = reddit.subreddit(sub)
            # top posts from this subreddit this year
            for submission in sub_reader.top(
                time_filter="year", limit=POST_LIMIT_PER_SUB
            ):
                # Then add the submission (post) text to the corpus.
                # I will not bother to keep trying until I reach
                # POST_LIMIT_PER_SUB and will just settle for what I find.
                if submission.selftext:
                    post_sentences = sent_tokenize(submission.selftext)
                    corpuses_by_subreddit_by_subject[subject][sub] += " ".join(post_sentences)

            sub_markovifier = markovify.Text(
                corpuses_by_subreddit_by_subject[subject][sub], state_size=STATE_SIZE
            )

            # Just generate sentences until we get one with desired start, if possible
            try:
                 sentence = sub_markovifier.make_sentence_with_start(
                    OTHER_PEOPLE_SHOULD, strict=False, tries=SENTENCE_GENERATION_ATTEMPTS
                 )
            except (KeyError, markovify.text.ParamError):
                continue
            if sentence:
                print(f"From {subject} subreddit r/{sub}: {sentence} \n")


if __name__ == "__main__":
    different_from_me_should()
