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
poem_id = [poem['_id'] for poem in poems_list]
poems_list.rewind()
poem_title = [poem['title'] for poem in poems_list]
poems_list.rewind()
poem_content = [poem['content'] for poem in poems_list]

tfidf = TfidfVectorizer(stop_words='english')

tfidf_matrix = tfidf.fit_transform(poem_content)

cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

# Construct a reverse map of indices and poem titles
indices = pd.Series(range(len(poem_title)), index=poem_title).drop_duplicates()

def get_recommendations(title, cosine_sim=cosine_sim):
   # Get the index of the movie that matches the title
    idx = indices[title]

    # Get the pairwsie similarity scores of all poems with that poem
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the poems based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar poems
    sim_scores = sim_scores[1:6]

    # Get the movie indices
    poem_indices = [i[0] for i in sim_scores]

    # Create a list of dictionaries with movie titles and similarity scores
    recommendations = [{'id': poem_id[i], 'title': poem_title[i], 'score': sim_scores[j][1]} for j, i in enumerate(poem_indices)]

    return recommendations

@app.route("/")
def hello_world():
    return "<p>This is a content-based recommendation system API for BreathingLines!</p>"

# Endpoint to get personalized feed for a user
@app.route("/personalized-feed/<user_id>", methods=['POST'])
def personalized_feed(user_id):
    # Fetch user's favorited poems list
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    favorited_poems_ids = user['favoritedPoems']

    # Check if the length of favorited_poems_ids is less than 10
    if len(favorited_poems_ids) < 4:
        return jsonify({'message': 'You have not interacted with poems much yet! Like more poems so we can show you more poems you might like!'}), 400

    # Get the last two elements of the favorited poems ids
    latest_ids = favorited_poems_ids[-10:]

    # Fetch favorited poems from MongoDB and give recommendations
    recommended_poems = []
    for poem_id in latest_ids:
        poem = poems_collection.find_one({'_id': poem_id})
        
        recommendations = get_recommendations(poem['title'])
        recommended_poems.append(recommendations)
    
    # Merge the recommendations
    merged_recommendations = {}
    for recommendations in recommended_poems:
        for recommendation in recommendations:
            title = recommendation['title']
            if title not in merged_recommendations:
                merged_recommendations[title] = recommendation

    # Convert the dictionary of merged recommendations back to a list
    final_recommendations = list(merged_recommendations.values())

    # Sort the recommendations by score in descending order
    final_recommendations = sorted(final_recommendations, key=lambda x: x['score'], reverse=True)

    # Update the user document in MongoDB with the final recommendations
    users_collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'poemRecommendations': final_recommendations}}
    )
        
    return json.loads(json_util.dumps(final_recommendations))


if __name__ == '__main__':
    app.run(debug=True)