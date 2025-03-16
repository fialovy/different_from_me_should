import re
import random

import markovify
import praw
import prawcore
from nltk.tokenize import sent_tokenize

from constants import (
    SUBREDDITS_BY_SUBJECT,
    POST_LIMIT_PER_SUB,
    OTHER_PEOPLE_SHOULD,
    STATE_SIZE,
    FORCED_SEEDS,
    SENTENCE_GENERATION_ATTEMPTS,
    MY_DUMB_INFINITE_LOOP_PREVENTER,
)


# i will make this modular later or never :P
def different_from_me_should():
    # Note that this uses a praw.ini in a separate config directory ($HOME/.config
    # for me on Linux). That is where the dfm_bot argument comes from, as
    # well as the user_agent and authentication creds.
    # See https://praw.readthedocs.io/en/stable/getting_started/configuration/prawini.html
    reddit = praw.Reddit("dfm_bot")
    for subject, subreddits in SUBREDDITS_BY_SUBJECT.items():
        print(f"***** SUBJECT: {subject}")
        for sub in subreddits:
            # Populate a corpus based on the body texts of this year's top posts
            # in the subreddit
            all_gathered_text_blobs = []
            try:
                sub_reader = reddit.subreddit(sub)
                # top posts from this subreddit this year
                for submission in sub_reader.top(
                    time_filter="year", limit=POST_LIMIT_PER_SUB
                ):
                    # Then add the submission (post) text to the blobs.
                    # I will not bother to keep trying until I reach
                    # POST_LIMIT_PER_SUB and will just settle for what I find.
                    if submission.selftext:
                        post_sentences = sent_tokenize(submission.selftext)
                        all_gathered_text_blobs.extend(post_sentences)
            except prawcore.exceptions.Forbidden:
                print(f"Got 403 when trying to access r/{sub}; skipping")
                continue

            # For each sub, we will also inject a number of 'arbitrary' sentences that
            # start with the desired prefix, since it is unlikely to be found directly
            # in the wild but markovify requires it to exist in the text.
            # The hope is that these sound generic enough to follow a
            # more telling statement that might be found in the posts and comments
            # (e.g., <some sentence characteristic of the sub> "Other people should
            # take this to heart.")
            num_blobs = len(all_gathered_text_blobs)
            seen_neighbor_indices = set()
            there_just_isnt_enough = 0
            for seed_sentence in FORCED_SEEDS:
                index_to_insert_at = random.randrange(num_blobs)
                while index_to_insert_at in seen_neighbor_indices and there_just_isnt_enough < MY_DUMB_INFINITE_LOOP_PREVENTER:
                    there_just_isnt_enough += 1
                    index_to_insert_at = random.randrange(num_blobs)
                # We don't want the seeds to end up too close together, so make a
                # decent range of indices around the current insert point become
                # off-limits. The negatives shouldn't do any harm here.
                seen_neighbor_indices.update([*range(index_to_insert_at-25, index_to_insert_at),
                    *range(index_to_insert_at, index_to_insert_at + 25)])
                all_gathered_text_blobs.insert(index_to_insert_at, seed_sentence)
            
            sub_corpus = " ".join(all_gathered_text_blobs)
            sub_markovifier = markovify.Text(
                sub_corpus, state_size=STATE_SIZE
            )
            # Just generate sentences until we get one with desired start, if possible
            try:
                sentence = sub_markovifier.make_sentence_with_start(
                    OTHER_PEOPLE_SHOULD,
                    strict=False,
                    tries=SENTENCE_GENERATION_ATTEMPTS,
                )
            except (KeyError, markovify.text.ParamError):
                continue
            if sentence:
                print(f"From {subject} subreddit r/{sub}: {sentence} \n")


if __name__ == "__main__":
    different_from_me_should()
