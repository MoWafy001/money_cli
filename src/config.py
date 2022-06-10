from dotenv import load_dotenv
import os

load_dotenv()


DATABASE_URI = os.environ['DATABASE_URI']
CURRENT_USER = os.environ['CURRENT_USER']
DEFAULT_CATEGORY_NAME = os.environ['DEFAULT_CATEGORY_NAME']