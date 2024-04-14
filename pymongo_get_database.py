from pymongo import MongoClient

def get_database():

   CONNECTION_STRING = "mongodb+srv://cppa123:blbycppa123@cluster0.4i6nlbd.mongodb.net/breathinglines?retryWrites=true&w=majority"
   
   client = MongoClient(CONNECTION_STRING)

   return client['breathinglines']

get_database()

if __name__ == "__main__":

   dbname = get_database()