import os
from dotenv import load_dotenv


ROOT_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(ROOT_DIR, "data")

load_dotenv()

DATABASE_CONFIG = {
    "host": os.getenv("DATABASE_HOST"),
    "database": os.getenv("DATABASE_NAME"),
    "user": os.getenv("DATABASE_USER"),
    "password": os.getenv("DATABASE_PASSWORD")
}

if __name__ == "__main__":
    print(ROOT_DIR)
    print(DATA_DIR)
    print(DATABASE_CONFIG)
