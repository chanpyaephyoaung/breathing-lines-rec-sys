# BreathingLines Recommender System API

## Introduction

This is a Flask-based API for a content-based recommender system designed for BreathingLines (https://github.com/chanpyaephyoaung/breathing-lines), a platform for sharing and discovering poetry. The API suggests personalized poem recommendations based on the user's interactions with previously favorited poems.

## Setup Instructions

1. Install Python (if not already installed).
2. Install the required Python packages using pip:
   ```bash
   pip freeze > requirements.txt
   ```
3. Make sure you have MongoDB installed and running locally, and create a database named 'breathinglines'.
4. Clone or download the project repository.

## Running the API

1. Navigate to the project directory.
2. Run the Flask application by executing the following command:
   ```bash
   python app.py
   ```
3. The API will start running locally on port 5000 by default.

## Endpoints

-  `/`: Home endpoint to verify the API is running.
-  `/personalized-feed/<user_id>` (POST): Endpoint to get personalized poem recommendations for a specific user. Requires the user's ID as a path parameter. Refer to your own database.

## Usage

-  Send a POST request to the `/personalized-feed/<user_id>` endpoint with the user's ID to receive personalized poem recommendations.
-  The API will return a JSON response containing the recommended poems along with their titles and similarity scores.
