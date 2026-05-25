import os
from dotenv import load_dotenv

load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "tiktok-reddit-trend-tool")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/trends.db")

DEFAULT_SUBREDDITS = [
    "AITAH",
    "AmItheAsshole",
    "relationship_advice",
    "TrueOffMyChest",
    "confession",
    "AskReddit",

    "NoSleep",
    "LetsNotMeet",
    "shortscarystories",

    "antiwork",
    "jobs",
    "careerguidance",
    "WorkReform",

    "personalfinance",
    "sidehustle",
    "povertyfinance",
    "frugal",

    "OutOfTheLoop",
    "popculturechat",

    "ChatGPT",
    "ArtificialInteligence",
    "technology",
    "InternetIsBeautiful",
]
