POST_LIMIT_PER_SUB = 500

DEFAULT_INCLUDE_COMMENTS = False

OTHER_PEOPLE_SHOULD = "Other people should"
#OTHER_PEOPLE_SHOULD = "People different from me should"

# Per markovify docs (https://pypi.org/project/markovify/#basic-usage), state
# size is "a number of words the probability of a next word depends on"
# So, ideally, I would like it to match my prefix, which should be quite short
STATE_SIZE = len(OTHER_PEOPLE_SHOULD.split(" "))

FORCED_SEED_SENTENCES = {
    f"{OTHER_PEOPLE_SHOULD} be aware.",
    f"{OTHER_PEOPLE_SHOULD} be aware of this.",
    f"{OTHER_PEOPLE_SHOULD} care about this.",
    f"{OTHER_PEOPLE_SHOULD} consider this.",
    f"{OTHER_PEOPLE_SHOULD} envision this.",
    f"{OTHER_PEOPLE_SHOULD} grok this.",
    f"{OTHER_PEOPLE_SHOULD} hear this.",
    f"{OTHER_PEOPLE_SHOULD} hear about this.",
    f"{OTHER_PEOPLE_SHOULD} imagine this.",
    f"{OTHER_PEOPLE_SHOULD} keep this in mind.",
    f"{OTHER_PEOPLE_SHOULD} know about this.",
    f"{OTHER_PEOPLE_SHOULD} know.",
    f"{OTHER_PEOPLE_SHOULD} know this.",
    f"{OTHER_PEOPLE_SHOULD} not forget about this.",
    f"{OTHER_PEOPLE_SHOULD} not forget this.",
    f"{OTHER_PEOPLE_SHOULD} notice this.",
    f"{OTHER_PEOPLE_SHOULD} see this.",
    f"{OTHER_PEOPLE_SHOULD} take this into consideration.",
    f"{OTHER_PEOPLE_SHOULD} take this to heart.",
    f"{OTHER_PEOPLE_SHOULD} talk about this.",
    f"{OTHER_PEOPLE_SHOULD} think about this.",
    f"{OTHER_PEOPLE_SHOULD} try to remember this.",
    f"{OTHER_PEOPLE_SHOULD} try to see this.",
    f"{OTHER_PEOPLE_SHOULD} try to understand this.",
    f"{OTHER_PEOPLE_SHOULD} understand this.",
}

SENTENCE_GENERATION_ATTEMPTS = 2000

MY_DUMB_INFINITE_LOOP_PREVENTER = SENTENCE_GENERATION_ATTEMPTS

SEED_INSERTION_WINDOW_SIZE = 25

MAX_COMMENTS_PER_POST = 3

MIN_COMMENT_LENGTH = 500  # in characters

SUBREDDITS_BY_SUBJECT = {
    "identity": {
        "autism",
        "aspergirls",
        "ftm",
        "MtF",
        "FTMMen",
        "asktransgender",
        "FTMOver30",
        "FTMOver50",
        "SpicyAutism",
        "adhdwomen",
        "ADHD",
        "TwoXChromosomes",
        "AskMen",
        "AskWomen",
        "MensRights",
    },
    "politics": {
        "trump",
        "SandersForPresident",
        "democrats",
        "Republican",
        "Conservative",
        "Libertarian",
    },
    "religion": {
        "hinduism",
        "Buddhism",
        "islam",
        "atheism",
        "agnostic",
        "Catholicism",
        "Baptist",
        "SouthernBaptist",
        "methodism",
        "mormon",
        "Anglicanism",
        "excatholic",
        "exmormon",
    },
}
