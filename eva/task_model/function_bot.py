import joblib
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


# Define the configuration data
config = {
    "music_model_path": "C:/Users/karan/Desktop/eva/task_model/file/music_recommendation_model.pkl",
    "music_tfidf_vectorizer_path": "C:/Users/karan/Desktop/eva/task_model/file/music_recommend_tfidf_vectorizer.pkl",
    "nltk_data_path": "C:/Users/karan/Desktop/eva/task_model/tokenizers",
}


# music files path
with open(config["music_model_path"], 'rb') as music_model_file:
    music_model = joblib.load(music_model_file)
with open(config["music_tfidf_vectorizer_path"], 'rb') as music_vect_file:
    music_tfidf_vectorizer = joblib.load(music_vect_file)


    

# Spotify API integration
data = pd.read_csv('C:/Users/karan/Desktop/eva/task_model/file/music_recommendation_dataset.csv')

client_id = '4afb3295ce3b4efbb48a2862ad03a9d4'
client_secret = '58c8a37749154466bcd2eb9116fe78cd'
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

# Function to recommend music based on user input
def recommend_music(cls, user_input, music_tfidf_vectorizer, music_model):

    # Predict genre using the trained model
    input_message_tfidf = music_tfidf_vectorizer.transform([user_input])
    predicted_genre = music_model.predict(input_message_tfidf)[0]

    # Get Spotify recommendations based on predicted genre
    genre_mapping = {code: genre for code, genre in enumerate(cls.data['Genre'].unique())}
    predicted_genre_name = genre_mapping[predicted_genre]
    results = cls.sp.search(q=f"genre:{predicted_genre_name}", type='track', limit=10)

    recommendations = []
    for track in results['tracks']['items']:
        recommendations.append({
            'Track': track['name'],
            'Artist': track['artists'][0]['name']
        })

    return recommendations