from importlib import metadata
from flask import Flask, request, jsonify
from flask_cors import CORS
from bson import ObjectId, json_util
import json
from pymongo_get_database import get_database
import pandas as pd
from pandas import DataFrame
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

app = Flask(__name__)
CORS(app)

# Connect to MongoDB
db = get_database()

# MongoDB collections
users_collection = db['users']
poems_collection = db['poems']

poems_list = poems_collection.find()
poem_title = [poemTitle['title'] for poemTitle in poems_list]
poems_list.rewind()
poem_content = [poem['content'] for poem in poems_list]
# print(poem_title[:3],  poem_content[:3])

tfidf = TfidfVectorizer(stop_words='english')

# poem_content = poem_content.fillna('')

tfidf_matrix = tfidf.fit_transform(poem_content)
# print(tfidf_matrix.shape)

cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
# print(cosine_sim.shape)
# print(cosine_sim[1])

# Construct a reverse map of indices and poem titles
indices = pd.Series(range(len(poem_title)), index=poem_title).drop_duplicates()
# print("suck it", indices[:3])

def get_recommendations(title, cosine_sim=cosine_sim):
   # Get the index of the movie that matches the title
    idx = indices[title]

    # Get the pairwsie similarity scores of all poems with that poem
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the poems based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar poems
    sim_scores = sim_scores[1:3]

    # Get the movie indices
    poem_indices = [i[0] for i in sim_scores]

    # Return the top 10 most similar poems
   #  return metadata['title'].iloc[movie_indices]

   # Create a list of dictionaries with movie titles and similarity scores
    recommendations = [{'title': poem_title[i], 'score': sim_scores[j][1]} for j, i in enumerate(poem_indices)]
    
    return json.dumps(recommendations)

print(get_recommendations('A Jelly-Fish'))

@app.route("/")
def hello_world():
    return "<p>This is a content-based recommendation system API for BreathingLines!</p>"

# Endpoint to get personalized feed for a user
@app.route("/personalized-feed/<user_id>")
def personalized_feed(user_id):
    # Fetch user's favorited poems list
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    favorited_poems_ids = user['favoritedPoems']

    # Fetch favorited poems from MongoDB
    favorited_poems = []
    for poem_id in favorited_poems_ids:
        poem = poems_collection.find_one({'_id': poem_id})
        favorited_poems.append(poem)
        
    return json.loads(json_util.dumps(favorited_poems))

if __name__ == '__main__':
    app.run(debug=True)
