POST_LIMIT_PER_SUB = 500

# Per markovify docs (https://pypi.org/project/markovify/#basic-usage), state
# size is "a number of words the probability of a next word depends on"
# So, ideally, I would like it to match my prefix, which should ideally be quite short
OTHER_PEOPLE_SHOULD = "Other people should"
# OTHER_PEOPLE_SHOULD = "People different from me should"

STATE_SIZE = len(OTHER_PEOPLE_SHOULD.split(" "))

FORCED_SEED_SENTENCES = {
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
    f"{OTHER_PEOPLE_SHOULD} take this to heart.",
    f"{OTHER_PEOPLE_SHOULD} take this into consideration.",
    f"{OTHER_PEOPLE_SHOULD} consider this.",
    f"{OTHER_PEOPLE_SHOULD} think about this.",
    f"{OTHER_PEOPLE_SHOULD} keep this in mind.",
    f"{OTHER_PEOPLE_SHOULD} shouldn't forget this.",
    f"{OTHER_PEOPLE_SHOULD} should know this.",
    f"{OTHER_PEOPLE_SHOULD} really need to know this.",
}

SENTENCE_GENERATION_ATTEMPTS = 1000

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
