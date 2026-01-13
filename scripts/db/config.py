import os
from dotenv import load_dotenv

load_dotenv()


def get_database_url() -> str:
    """
    Returns the database url from the environment variables
    """
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set. Add it to your .env")
    return url
