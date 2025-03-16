import random
import re

import markovify
import praw
import prawcore
from nltk.tokenize import sent_tokenize

from constants import (FORCED_SEED_SENTENCES, MAX_COMMENTS_PER_POST,
                       MIN_COMMENT_LENGTH, MY_DUMB_INFINITE_LOOP_PREVENTER,
                       OTHER_PEOPLE_SHOULD, POST_LIMIT_PER_SUB,
                       SEED_INSERTION_WINDOW_SIZE,
                       SENTENCE_GENERATION_ATTEMPTS, STATE_SIZE,
                       SUBREDDITS_BY_SUBJECT)


# i will make this modular later or never :P
def different_from_me_should():
    # Note that this uses a praw.ini in a separate config directory ($HOME/.config
    # for me on Linux). That is where the dfm_bot argument comes from, as
    # well as the user_agent and authentication creds.
    # See https://praw.readthedocs.io/en/stable/getting_started/configuration/prawini.html
    reddit = praw.Reddit("dfm_bot")
    for subject, subreddits in SUBREDDITS_BY_SUBJECT.items():
        for subreddit in subreddits:
            # Populate a corpus based on the body texts of this year's top posts
            # in the subreddit
            all_gathered_text_blobs = []
            try:
                sub_reader = reddit.subreddit(subreddit)
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
                        # Ideally we can add a couple of top comments and replies as well
                        # See https://praw.readthedocs.io/en/stable/tutorials/comments.html
                        # TODO: UNTIL max, not UP TO max
                        submission.comment_sort = "top"
                        for comment in submission.comments.list()[
                            :MAX_COMMENTS_PER_POST
                        ]:
                            if len(comment.body) >= MIN_COMMENT_LENGTH:
                                comment_sentences = sent_tokenize(comment.body)
                                all_gathered_text_blobs.extend(comment_sentences)
            except prawcore.exceptions.Forbidden:
                print(f"Got 403 when trying to access r/{subreddit}; skipping")
                continue

            if not all_gathered_text_blobs:
                print(f"Can't gather enough text from r/{subreddit}; skipping")

            # For each subreddit, we will also inject a number of 'arbitrary' sentences that
            # start with the desired prefix, since it is unlikely to be found directly
            # in the wild but markovify requires it to exist in the text.
            # The hope is that these sound generic enough to follow a
            # more telling statement that might be found in the posts and comments
            # (e.g., <some sentence characteristic of the subreddit> "Other people should
            # take this to heart.")
            num_blobs = len(all_gathered_text_blobs)
            seen_neighbor_indices = set()
            there_just_isnt_enough = 0
            for seed_sentence in FORCED_SEED_SENTENCES:
                index_to_insert_at = random.randrange(num_blobs)
                while (
                    index_to_insert_at in seen_neighbor_indices
                    and there_just_isnt_enough < MY_DUMB_INFINITE_LOOP_PREVENTER
                ):
                    there_just_isnt_enough += 1
                    index_to_insert_at = random.randrange(num_blobs)
                # We don't want the seeds to end up too close together, so make a
                # decent range of indices around the current insert point become
                # off-limits. The negatives shouldn't do any harm here.
                seen_neighbor_indices.update(
                    [
                        *range(
                            index_to_insert_at - SEED_INSERTION_WINDOW_SIZE,
                            index_to_insert_at,
                        ),
                        *range(
                            index_to_insert_at,
                            index_to_insert_at + SEED_INSERTION_WINDOW_SIZE,
                        ),
                    ]
                )
                all_gathered_text_blobs.insert(index_to_insert_at, seed_sentence)

            subreddit_corpus = " ".join(all_gathered_text_blobs)
            subreddit_markovifier = markovify.Text(
                subreddit_corpus, state_size=STATE_SIZE
            )
            # Just generate sentences until we get one with desired start, if possible
            try:
                sentence = subreddit_markovifier.make_sentence_with_start(
                    OTHER_PEOPLE_SHOULD,
                    strict=False,
                    tries=SENTENCE_GENERATION_ATTEMPTS,
                )
            except (KeyError, markovify.text.ParamError):
                continue
            if sentence:
                print(f"From {subject} subreddit r/{subreddit}: {sentence} \n")


if __name__ == "__main__":
    different_from_me_should()
