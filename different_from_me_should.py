import random
import re

import markovify
import praw
import prawcore
from nltk.tokenize import sent_tokenize

# maybe make these more configurable and class-associated one day
from constants import (
    DEFAULT_INCLUDE_COMMENTS,
    FORCED_SEED_SENTENCES,
    MAX_COMMENTS_PER_POST,
    MIN_COMMENT_LENGTH,
    MY_DUMB_INFINITE_LOOP_PREVENTER,
    OTHER_PEOPLE_SHOULD,
    POST_LIMIT_PER_SUB,
    SEED_INSERTION_WINDOW_SIZE,
    SENTENCE_GENERATION_ATTEMPTS,
    STATE_SIZE,
    SUBREDDITS_BY_SUBJECT,
)


class DifferentFromMeShould:
    def __init__(self):
        # Note that this uses a praw.ini in a separate config directory ($HOME/.config
        # for me on Linux via Windows Subsystem for Linux). That is where the dfm_bot
        # argument comes from, as well as the user_agent and authentication credentials.
        # See https://praw.readthedocs.io/en/stable/getting_started/configuration/prawini.html
        self.reddit = praw.Reddit("dfm_bot")

    def generate_new_sentence_from_subreddit(self, subreddit, include_comments=False):
        existing_subreddit_sentences = (
            self.obtain_existing_subreddit_sentences_from_subreddit(
                subreddit, include_comments=include_comments
            )
        )
        if not existing_subreddit_sentences:
            return f"Can't gather enough text from r/{subreddit}; we cannot generate a sentence."

        combined_sentences = (
            self.inject_seed_sentences_into_existing_subreddit_sentences(
                existing_subreddit_sentences
            )
        )
        new_sentence, success = self.generate_new_sentence_with_desired_start(
            combined_sentences
        )

        if not success:
            return f"Can't generate a sentence from r/{subreddit}: error was {new_sentence if new_sentence else 'unknown/probably just us not meeting markovify requirements.'}"
        return new_sentence

    def obtain_existing_subreddit_sentences_from_subreddit(
        self, subreddit, include_comments=False
    ):
        """
        Populate a corpus based on the body texts of this year's top posts in the subreddit
        """
        existing_subreddit_sentences = []
        try:
            sub_reader = self.reddit.subreddit(subreddit)
            for submission in sub_reader.top(
                time_filter="year", limit=POST_LIMIT_PER_SUB
            ):
                # I will not bother to keep trying until I reach
                # POST_LIMIT_PER_SUB and will just settle for what I find.
                if submission.selftext:
                    post_sentences = sent_tokenize(submission.selftext)
                    existing_subreddit_sentences.extend(post_sentences)
                    # If desired we can add a couple of top comments and replies as well
                    # But this appears to be pretty slow
                    # See https://praw.readthedocs.io/en/stable/tutorials/comments.html
                    if include_comments:
                        submission.comment_sort = "top"
                        found_comments = 0
                        for comment in submission.comments.list():
                            if (
                                found_comments < MAX_COMMENTS_PER_POST
                                and len(comment.body) >= MIN_COMMENT_LENGTH
                            ):
                                comment_sentences = sent_tokenize(comment.body)
                                existing_subreddit_sentences.extend(comment_sentences)
                                found_comments += 1
        except prawcore.exceptions.Forbidden:
            print(f"Got 403 when trying to access r/{subreddit}; skipping")
            return existing_subreddit_sentences

        return existing_subreddit_sentences

    def inject_seed_sentences_into_existing_subreddit_sentences(
        self, existing_subreddit_sentences
    ):
        """
        For each subreddit, we will also inject a number of 'arbitrary' sentences that
        start with the desired prefix, since it is unlikely to be found directly
        in the wild but the desired markovify util requires it to exist in the text.
        The hope is that these sound generic enough to follow a
        more telling statement that might be found in the posts and comments
        (e.g., <some sentence characteristic of the subreddit> "Other people should
        take this to heart.")
        I am not a data scientist and haven't taken Cav's class since 2013, so
        this could in fact be meaningless fun.
        """
        num_blobs = len(existing_subreddit_sentences)
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
            existing_subreddit_sentences.insert(index_to_insert_at, seed_sentence)

        return existing_subreddit_sentences

    def generate_new_sentence_with_desired_start(self, combined_sentences):
        corpus = " ".join(combined_sentences)
        markovifier = markovify.Text(corpus, state_size=STATE_SIZE)
        # Just generate sentences until we get one with desired start, if possible
        try:
            sentence = markovifier.make_sentence_with_start(
                OTHER_PEOPLE_SHOULD,
                strict=False,
                tries=SENTENCE_GENERATION_ATTEMPTS,
            )
        except (KeyError, markovify.text.ParamError) as err:
            return f"Can't generate sentence with desired start: (err)", False
        return sentence, True if sentence else False


def run_generate_new_sentence_for_all_subreddits_by_subject():
    sentence_generator = DifferentFromMeShould()
    for subject, subreddits in SUBREDDITS_BY_SUBJECT.items():
        for subreddit in subreddits:
            sentence = sentence_generator.generate_new_sentence_from_subreddit(
                subreddit, include_comments=DEFAULT_INCLUDE_COMMENTS
            )
            print(f"From {subject} subreddit r/{subreddit}: {sentence} \n")


if __name__ == "__main__":
    run_generate_new_sentence_for_all_subreddits_by_subject()
