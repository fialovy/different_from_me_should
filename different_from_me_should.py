import re
from pathlib import Path

import markovify
import praw

POST_LIMIT_PER_SUB = 100
MIN_POST_OR_COMMENT_LENGTH = 50
# Per markovify docs (https://pypi.org/project/markovify/#basic-usage), state
# size is "a number of words the probability of a next word depends on"
OTHER_PEOPLE_SHOULD = "Other people should"
STATE_SIZE = len(OTHER_PEOPLE_SHOULD)
FORCED_SEEDS = {
    f"{OTHER_PEOPLE_SHOULD} do this.\n",
    f"{OTHER_PEOPLE_SHOULD} be kinder.\n",
    f"{OTHER_PEOPLE_SHOULD} understand this.\n",
    f"{OTHER_PEOPLE_SHOULD} work toward this.\n",
    f"{OTHER_PEOPLE_SHOULD} notice this.\n",
    f"{OTHER_PEOPLE_SHOULD} try this.\n",
    f"{OTHER_PEOPLE_SHOULD} do better.\n",
    f"{OTHER_PEOPLE_SHOULD} get involved.\n",
    f"{OTHER_PEOPLE_SHOULD} be more aware of this.\n",
    f"{OTHER_PEOPLE_SHOULD} care about this.\n",
}
SENTENCE_GENERATION_ATTEMPTS = 1000


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
            sub_reader = reddit.subreddit(sub)
            # top posts from this subreddit this year
            for submission in sub_reader.top(
                time_filter="year", limit=POST_LIMIT_PER_SUB
            ):
                # Seed the sub corpus with a huge number of 'neutral'-sounding sentences that
                # start with my desired prefix
                for seed_sentence in FORCED_SEEDS:
                    corpuses_by_subreddit[sub] += seed_sentence
                # Then add the submission (post) text to the corpus.
                # I will not bother to keep trying until I reach
                # POST_LIMIT_PER_SUB and will just settle for what I find.
                if len(submission.selftext) >= MIN_POST_OR_COMMENT_LENGTH:
                    newline_delimited_post_text = (
                        submission.selftext.replace(".", "\n") + "\n"
                    )
                    corpuses_by_subreddit[sub] += newline_delimited_post_text

            sub_markovifier = markovify.NewlineText(
                corpuses_by_subreddit[sub], state_size=STATE_SIZE
            )
            # Just generate sentences until we get one with desired start, if possible
            for _ in range(SENTENCE_GENERATION_ATTEMPTS):
                try:
                    sentence = sub_markovifier.make_sentence_with_start(
                        OTHER_PEOPLE_SHOULD, strict=False
                    )
                except:
                    continue
                if sentence:
                    print(f"From {subject} subreddit r/{sub}: " + sentence + "\n")


if __name__ == "__main__":
    different_from_me_should()
