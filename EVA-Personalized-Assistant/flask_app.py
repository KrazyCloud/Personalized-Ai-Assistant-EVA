from flask import Flask, request, render_template
import subprocess
import numpy as np
import speech_recognition as sr
import pyttsx3
import openai
import requests
import webbrowser
import wikipediaapi
import datetime  # Import the datetime module
import joblib
import numpy as np


app = Flask(__name__)

# Replace 'YOUR_API_KEY' with your actual OpenAI API key
api_key = 'Your API key here'

# Initialize the OpenAI API client
openai.api_key = api_key

# Initialize the speech recognition and text-to-speech engines
recognizer = sr.Recognizer()
engine = pyttsx3.init()

voices = engine.getProperty('voices')
eva_voice = None

# Find the eva voice
for voice in voices:
    if voice.name == 'Microsoft Zira Desktop - English (United States)':
        eva_voice = voice
        break

# Set the voice of the engine to eva
if eva_voice is not None:
    engine.setProperty('voice', eva_voice.id)

# Define the chatbot's responses
GREETINGS = ["Hello! Sir", "How may I help you Sir?", "Hi Sir, welcome back!", "Hello Sir, I was waiting for you to join!"]
response = ["Hi there! As an AI language model, I don't have the ability to do things like humans do. However, I'm always here and ready to chat with you and assist you in any way I can. Is there something specific you would like to talk about or ask me?", "I'm a AI assiatance that will help you in doing tasks"]
GOODBYES = ["Goodbye!", "See you later!", "Farewell!"]
HELP_RESPONSE = "You can ask me to add tasks, list tasks, remove tasks, search on Google, or get news."
features = ['Creating to-do-list', 'Search on google', 'playing songs', 'Get news']
intro = ['Hi', 'Hey', 'Hello', "What up"]
info = ['information', 'info', 'tell', 'what is']

    
# Function to recognize speech and return recognized text
def recognize_speech(voice_input=None):
    if voice_input is None:
        with sr.Microphone() as source:
            print("Listening...")
            try:
                audio = recognizer.listen(source)
                user_input = recognizer.recognize_google(audio).strip()
                return user_input
            except sr.UnknownValueError:
                print("Sorry, I could not understand your audio.")
                return None
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                return None
    else:
        # Process the provided 'voice_input' argument and return the recognized text
        # Replace this with your actual speech recognition implementation
        recognized_text = voice_input  # Placeholder for custom processing
        return recognized_text

# Function to convert text to speech
def text_to_speech(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in text-to-speech: {e}")

# Function to greet based on the time of day
def wish_me():
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    hour = now.hour
    if hour >= 0 and hour < 12:
        return f"Good morning! It's {current_time}"
    elif hour >= 12 and hour < 18:
        return f"Good afternoon! It's {current_time}"
    else:
        return f"Good evening! It's {current_time}"

# Function to play a song on YouTube
def play_song(song_name):
    query = song_name
    url = f"https://www.youtube.com/results?search_query={query}"
    response = requests.get(url)
    search_results = response.text

    # Find the first video link from the search results
    video_link_start = search_results.find('/watch?v=')
    if video_link_start != -1:
        video_link_end = search_results.find('"', video_link_start)
        video_link = search_results[video_link_start:video_link_end]
        video_url = f"https://www.youtube.com{video_link}"
        webbrowser.open(video_url)
        return f"Playing '{song_name}' on YouTube..."
    else:
        return f"No search results found for '{song_name}'."

# Initialize the Wikipedia API client with a user agent
wiki_wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent='MyWikipediaBot/1.0'
)

# Function to get Wikipedia information
def get_wikipedia_info(query):
    try:
        page = wiki_wiki.page(query)
        if page.exists():
            summary = page.summary[:500]  # Limit the summary to 500 characters
            return summary
        else:
            return "Sorry, I couldn't find any information on that topic."
    except Exception as e:
        return str(e)

# Function to get news articles
def get_news(query):
    API_KEY = 'a6ed1e73fd5e4897b6dccdb8d78963ff'  # Replace with your actual News API key
    url = f"https://newsAPI.org/v2/everything?q={query}&APIKey={API_KEY}"
    response = requests.get(url)
    news_data = response.json()
    articles = news_data['articles']
    if len(articles) > 0:
        num_articles = min(3, len(articles))
        news_list = []
        for article in range(num_articles):
            article = articles[article]
            title = article['title']
            description = article['description']
            source = article['source']['name']
            news_list.append({
                'title': title,
                'description': description,
                'source': source
            })
        return news_list
    else:
        return "No news articles found."



    
    # Load the saved TF-IDF model and associated preprocessing objects
model_filename = r'C:\Practice\EVA\models\todo_list_model.pkl'
loaded_model = joblib.load(model_filename)

# Load the saved TF-IDF vectorizer and label encoder
tfidf_vectorizer = joblib.load(r'C:\Practice\EVA\models\todo_list_tfidf_vectorizer.pkl')
label_encoder = joblib.load(r'C:\Practice\EVA\models\todo_list_label_encoder.pkl')

# Initialize an empty list to store items
todo_list = []

# Function to save the to-do list to a text file
def save_to_file(todo_list):
    with open('todo_list.txt', 'w') as file:
        for item in todo_list:
            file.write(item + '\n')

# Function to load the to-do list from the text file
def load_from_file():
    try:
        with open('todo_list.txt', 'r') as file:
            lines = file.read().splitlines()
            return lines
    except FileNotFoundError:
        return []

# Function to extract and remove an item from the list
def extract_item(words, idx):
    if idx < len(words):
        if words[idx] == "and":
            return extract_item(words, idx + 1)
        return words[idx], words[:idx] + words[idx + 1:]
    return None, words

# Function to delete items from the list
def delete_item(item):
    if item in todo_list:
        todo_list.remove(item)
        print(f"Deleted: {item}")
    else:
        print(f"{item} not found in the list.")

# Function for number to word
def word_to_number(word):
    word = word.lower()
    numbers = {
        'one': 1,
        'first': 1,
        'two': 2,
        'second': 2,
        'three': 3,
        'third': 3,
        'four': 4,
        'fourth': 4,
        'five': 5,
        'fifth': 5,
        'six': 6,
        'sixth': 6,
        'seven': 7,
        'seventh': 7,
        'eight': 8,
        'eighth': 8,
        'nine': 9,
        'ninth': 9,
    }
    return numbers.get(word, -1)  # Return -1 if not found

def to_do_list(user_input):
    # Load the initial list from the text file
    todo_list = load_from_file()

    # Preprocess the input using TF-IDF vectorizer
    new_message_tfidf = tfidf_vectorizer.transform([user_input])

    # Predict intent using the loaded model
    predicted_class_encoded = loaded_model.predict(new_message_tfidf)
    predicted_class = label_encoder.inverse_transform(predicted_class_encoded)

    resonse = ""
# Splitthe input into words for further processing
    words = user_input.lower().split()
    # Perform actions based on predicted intent
    if predicted_class[0] == 'add':
        if 'add ' in user_input:
            items = user_input.split('add ')[1].split(', ')
            todo_list.extend(items)
            save_to_file(todo_list)  # Save the updated list
            print("Bot: Added to the list:", ', '.join(items))
        else:
            print("Bot: Please specify items to add.")
    elif predicted_class[0] == 'view':
        if len(todo_list) > 0:
            print("Bot: To-do list:")
            for idx, item in enumerate(todo_list, start=1):
                print(f"{idx}. {item}")
        else:
            print("Bot: The to-do list is empty.")
    elif predicted_class[0] == 'delete':
        if len(words) > 1:
            target = words[1].strip()
            target_num = word_to_number(target)  # Convert word to number
            if target.isdigit():  # Check if the input is a number
                index = int(target) - 1
                if 0 <= index < len(todo_list):
                    delete_item(todo_list[index])
                else:
                    print("Invalid item index.")
            elif target_num != -1:  # Check if the word represents a valid number
                if 1 <= target_num <= len(todo_list):
                    delete_item(todo_list[target_num - 1])
                else:
                    print("Invalid position.")
            else:
                deleted = False
                for item in todo_list[:9]:
                    if target in item.lower():
                        delete_item(item)
                        deleted = True
                        break
                if not deleted:
                    print(f"{target} not found in the list.")
        else:
            print("Invalid input for deletion.")
    elif predicted_class[0] == 'exit':
        print("Bot: Exiting the interaction.")
    else:
        print("Bot: I'm not sure how to respond to that.")

    return response

# Websearch class
def search_google(query):
    query = query.replace(' ', '+')
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)

# Function to chat with GPT-3
def chat_with_gpt3(prompt):
    # Define the prompt for the conversation
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]

    try:
        # Generate a response from the assistant
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation
        )

        # Extract and return the assistant's reply
        assistant_reply = response['choices'][0]['message']['content']
        return assistant_reply
    except Exception as e:
        return str(e)



# Main loop for interacting with the chatbot
text_to_speech(f"{wish_me()}\nEVA is here for your service. What would you like to do today?")

# Route to render the HTML page with the voice button
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle voice input and display chatbot responses
@app.route('/chat', methods=['POST'])
def chat():
    voice_input = request.form['voice_input'].lower()  # Convert user input to lowercase for case-insensitive checks
    print("You (Voice):", voice_input)
    
    # Check for the "todo" command and handle it separately
    if 'todo' in voice_input:
        # Extract the to-do list command from the user input (e.g., "todo xyz")
        todo_command = voice_input.replace('todo', '').strip()
        response = to_do_list(todo_command)
    else:
        # If the input is not a "todo" command, proceed with chat GPT
        # Check for specific keywords and route to the corresponding function
        if 'play' in voice_input:
            # Extract the song name from the user input (e.g., "play xyz")
            song_name = voice_input.replace('play', '').strip()
            response = play_song(song_name)
        elif 'wiki' in voice_input:
            # Extract the query for Wikipedia from the user input (e.g., "wiki xyz")
            wiki_query = voice_input.replace('wiki', '').strip()
            response = get_wikipedia_info(wiki_query)
        elif 'search' in voice_input:
            # Extract the query for Wikipedia from the user input (e.g., "wiki xyz")
            search_query = voice_input.replace('search', '').strip()
            response = search_google(search_query)
            text_to_speech('Searching on google')
        elif 'news' in voice_input:
            # Extract the query for news from the user input (e.g., "news xyz")
            news_query = voice_input.replace('news', '').strip()
            response = get_news(news_query)
        else:
            # If none of these keywords are found, continue with the general chat function
            response = chat_with_gpt3(voice_input)
    
    # Convert the response to speech and play it
    text_to_speech(response)
    
    return response

if __name__ == '__main__':
    app.run(debug=True)