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


# i will make this modular later :P
def different_from_me_should():
    # Note that this uses a praw.ini in a separate config directory ($HOME/.config
    # for me on Linux). That is where the dfm_bot argument comes from, as
    # well as the user_agent and authentication creds.
    # See https://praw.readthedocs.io/en/stable/getting_started/configuration/prawini.html
    corpuses_by_subreddit_by_subject = {
        subreddit_subject: {
            subreddit: "" for subreddit in subreddits}
           for subreddit_subject, subreddits in SUBREDDITS_BY_SUBJECT.items()
    }
    # Populate a corpus based on this year's top posts and/or comments
    reddit = praw.Reddit("dfm_bot")
    for subject, corpuses_by_subreddit in corpuses_by_subreddit_by_subject.items():
        print(f"***** SUBJECT: {subject}")
        for sub in corpuses_by_subreddit:
            all_gathered_text_blobs = []
            # For each sub, we will also throw in a number of 'arbitrary' sentences that
            # start with the desired prefix, since it is unlikely to be found directly
            # in the wild. The hope is that these sound generic enough to follow a
            # more telling statement that might be found in the posts and comments
            # (e.g., <some sentence characteristic of the sub> "Other people should
            # take this to heart.")
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
                        #corpuses_by_subreddit_by_subject[subject][sub] += " ".join(
                        #    post_sentences
                        #)
                        # We want to keep multiple sentences in a row together
                        # and then randomly stick in the seed things
                        all_gathered_text_blobs.extend(post_sentences)
            except prawcore.exceptions.Forbidden:
                print(f"Got 403 when trying to access r/{sub}; skipping")
                continue

            # Inject seed sentences at random places in the list of gathered
            # reddit sentences, preferably not next to each other
            num_blobs = len(all_gathered_text_blobs)
            seen_neighbor_indices = set()
            there_just_isnt_enough = 0
            for seed_sentence in FORCED_SEEDS:
                index_to_insert_at = random.randrange(num_blobs)
                while index_to_insert_at in seen_neighbor_indices and there_just_isnt_enough < MY_DUMB_INFINITE_LOOP_PREVENTER:
                    there_just_isnt_enough += 1
                    index_to_insert_at = random.randrange(num_blobs)
                # should increase this window probably
                seen_neighbor_indices.update({index_to_insert_at - 1, index_to_insert_at, index_to_insert_at + 1})
                all_gathered_text_blobs.insert(index_to_insert_at, seed_sentence)
            #for seed_sentence in FORCED_SEEDS:
            #    all_gathered_text_blobs.append(seed_sentence)
            #    #corpuses_by_subreddit_by_subject[subject][sub] += f"{seed_sentence} "
            
            sub_corpus = " ".join(all_gathered_text_blobs)
            import pdb; pdb.set_trace() 
            sub_markovifier = markovify.Text(
                #corpuses_by_subreddit_by_subject[subject][sub], state_size=STATE_SIZE
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
