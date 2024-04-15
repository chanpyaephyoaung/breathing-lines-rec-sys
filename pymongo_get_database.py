from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from pymongo import MongoClient

def get_database():

   CONNECTION_STRING = os.environ.get("MONGODB_ATLAS_URI")
   
   client = MongoClient(CONNECTION_STRING)

   return client['breathinglines']

get_database()

if __name__ == "__main__":

   dbname = get_database()