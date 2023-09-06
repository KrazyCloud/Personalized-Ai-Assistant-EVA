import random
from spellchecker import SpellChecker
import webbrowser
import requests
import datetime
import wikipedia
import nltk
from flask import Flask, render_template, request, jsonify
from task_bot.function_bot import music_recommender
from task_bot.model import predict_intent

# Download the missing nltk resource
#python3.10 -m spacy download en_core_web_sm
nltk.download('punkt')

app = Flask(__name__)

# Initialize the spell checker
spell = SpellChecker()

# Define your global variables and responses here
GREETINGS = ["Hello! Sir", "How may I help you Sir?", "Hi Sir, welcome back!", "Hello Sir, I was waiting for you to join!"]
question = ["Hi there! As an AI language model, I don't have the ability to do things like humans do. However, I'm always here and ready to chat with you and assist you in any way I can. Is there something specific you would like to talk about or ask me?", "I'm an AI assistant that will help you in doing tasks"]
GOODBYES = ["Goodbye!", "See you later!", "Farewell!"]
HELP_RESPONSE = "You can ask me to add tasks, list tasks, remove tasks, search on Google, or get news."
features = ['Creating to-do-list', 'Search on google', 'playing songs', 'Get news']
intro = ['hi', 'hey', 'hello', "what's up"]
info = ['information', 'info', 'tell', 'who']
search_keywords = ['search', 'google']
exit_keywords = ["exit", "quit", "goodbye", "bye", "sleep", "end", "close", "stop", "finish", "terminate"]
exit_responses = ["Goodbye!","See you later!","Farewell!","If you have any more questions in the future, don't hesitate to return. Goodbye!","Until next time!","Take care!","Have a great day!","Thanks for chatting with me. Goodbye!","It's been a pleasure assisting you. Goodbye!","Remember, I'm just a message away if you need help later. Goodbye!"]
todo_list_variations = ["to-do list", "todo list", "tasks", "task list", "my tasks", "my to-do list"]
identity_keywords = ["who are you", "what's your name", "tell me about yourself"]
identity_responses = [
    "I am an AI language model created by OpenAI. You can call me ChatGPT.",
    "I'm ChatGPT, a language model here to assist you with information and tasks.",
    "I don't have a personal identity, but I'm here to help answer your questions and provide assistance.",
]
wellbeing_keywords = ["how are you", "are you okay", "how's it going"]
wellbeing_responses = [
    "I don't have feelings or emotions, but I'm ready to assist you!",
    "I'm just a program, so I don't have feelings, but thank you for asking. How can I assist you today?",
    "I'm here and fully operational, ready to help with any questions or tasks you have.",
]
# Define your functions and classes from task_bot.py here

# Websearch class
def search_google(query):
    query = query.replace(' ', '+')
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)


def get_wikipedia_info(query):
    try:
        results = wikipedia.summary(query, sentences=2)
        return "According to Wikipedia\n" + results
    except wikipedia.exceptions.PageError as e:
        return f"I couldn't find any information on '{query}'."

def play_song(song_name):
    query = song_name.replace(' ', '+')
    url = f"https://www.youtube.com/results?search_query={query}"
    response = requests.get(url)
    search_results = response.text

    video_link_start = search_results.find('/watch?v=')
    if video_link_start != -1:
        video_link_end = search_results.find('"', video_link_start)
        video_link = search_results[video_link_start:video_link_end]
        video_url = f"https://www.youtube.com{video_link}"
        webbrowser.open(video_url)

# API class
def get_news(query):
    API_KEY = '7819c885b0ef4c659fb719c35170a211'  # Replace with your actual API key
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
        return ["No news articles found."]


# Command class
dialogues = {}

def wishMe():
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Hello Sir, Good Morning"
    elif hour < 18:
        return "Hello Sir, Good Afternoon"
    else:
        return "Hello Sir, Good Evening"

def timeMe():
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Good Morning"
    elif hour < 18:
        return "Good Afternoon"
    else:
        return "Good Evening"

# Initialize the tasks list as a global variable
tasks = []

# Define a function to generate a response from the chatbot
def generate_response(user_input):

    global tasks

    while True:
        user_input = autocorrect_user_input(user_input)
        # Command to generate a response
        user_input = user_input.lower()
        intent = predict_intent(user_input)

        if user_input is not None:
            user_input = user_input.lower()

 # first interaction with bot
        if any(word in user_input for word in intro):
            return random.choice(GREETINGS)

        # Check if the user's query matches any identity-related keyword.
        elif any(keyword in user_input for keyword in identity_keywords):
            response = random.choice(identity_responses)
# Check if the user's query matches any well-being-related keyword.
        elif any(keyword in user_input for keyword in wellbeing_keywords):
            response = random.choice(wellbeing_responses)
        elif:
            response = "I'm here to assist you. Is there anything specific you'd like to know or discuss?"
 # greeting
        elif "good morning" in user_input:
            current_hour = datetime.datetime.now().hour
            if current_hour < 12:
                return "Good Morning"
            else:
                return "Sorry, it's not morning anymore\n" + wishMe()

        elif "good afternoon" in user_input:
            current_hour = datetime.datetime.now().hour
            if 12 <= current_hour < 18:
                return "Good Afternoon"
            else:
                return "Sorry, it's not afternoon anymore\n" + wishMe()

        elif "good evening" in user_input:
            current_hour = datetime.datetime.now().hour
            if current_hour >= 18:
                return "Good Evening"
            else:
                return "Sorry, it's not evening yet\n" + wishMe()

 # info about time
        elif "time" in user_input:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            return f"The current time is {current_time}...\n{timeMe()} Sir"


# listing bot features
        elif "feature" in user_input or "features" in user_input:
            features_list = '\n'.join([f"{i + 1}. {feature}" for i, feature in enumerate(features)])
            return f"The available features are:\n{features_list}"

# get out from bot saying goodbye
        elif "goodbye" in user_input or "bye" in user_input:
            return random.choice(GOODBYES)

# help area
        elif "help" in user_input:
            return HELP_RESPONSE
        
# Inside generate_response function
        elif "create to do list" in user_input:
            return "What are the task you want to add the To-DO List?"

        elif "add" in user_input:
            task = user_input.replace("add", "").strip()
            if task:
                tasks.append(task)
                return f"Task '{task}' has been added to the to-do list."
            else:
                return "Please provide a task to add."

        elif "delete" in user_input and "to do list" in user_input:
            task_to_delete = user_input.replace("delete", "").replace("from to do list", "").strip()
            if task_to_delete:
                if task_to_delete in tasks:
                    tasks.remove(task_to_delete)
                    return f"Task '{task_to_delete}' has been deleted from the to-do list."
                else:
                    return f"Task '{task_to_delete}' not found in the to-do list."
            else:
                return "Please provide a task description to delete from the to-do list."

                
        elif "list" in user_input:
            if not tasks:
                return "The to-do list is empty."
            else:
                task_list = "\n".join([f"{i + 1}. {task}" for i, task in enumerate(tasks)])
                return f"Here is your to-do list:\n{task_list}"
        

# search in google
        elif any(keyword in intent.lower() for keyword in search_keywords):
            query = user_input.replace("search", "").strip()
            if query:
                search_google(query)
                return f"Searching Google for '{query}'..."
            else:
                return "Please provide a query to search on Google."
        
# searching for info
        elif any(keyword in intent.lower() for keyword in intro):
            query = user_input.replace("info", "").strip()
            if query:
                response = get_wikipedia_info(query)
                return response
            else:
                return "Please provide a query for information."
            

        elif "news" in intent:
            query = user_input.replace("news", "").strip()
            if query:
                news_articles = get_news(query)
                if news_articles:
                    response = "Here are some news articles:\n\n"
                    for article in news_articles:
                        response += f"Title: {article['title']}\nDescription: {article['description']}\nSource: {article['source']}\n\n"
                    return response
                else:
                    response = "No news articles found."
                    return response
            else:
                return "Please provide a query to get news."

        elif "play" in intent:
            song_name = user_input.replace("play", "").strip()
            if song_name:
                play_song(song_name)
                return f"Playing '{song_name}' on YouTube..."
            else:
                return "Please provide the name of the song to play."

        # Additional functionalities can be added here
        elif "recommend" in intent:
            song_recommendation = music_recommender(user_input)
            if song_recommendation:
                response = "Here are some recommended songs:\n\n"
                for song in song_recommendation:
                    response += f"Track: {song['Track']}\nArtist: {song['Artist']}\n\n"
                
                # Play the first recommended song on YouTube (you can modify this part)
                if song_recommendation[0]:
                    play_song(song_recommendation[0]['Track'])
                
                return response
            else:
                return "No song recommendations found."
        elif user_input in exit_keywords:
            exit(0)

# Autocorrect user input
def autocorrect_user_input(user_input):
    if user_input is not None and user_input.strip():
        words = user_input.split()
        corrected_words = [spell.correction(word) for word in words]
        return ' '.join(corrected_words)
    else:
        return user_input  # Return the input as is if it's None or empty

# Define your predict_intent and load_models functions from model.py here


# Define your routes for Flask here

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.form.get('user_input')
    response = generate_response(user_input)
    if response != "null":
        return jsonify({"response": response})
    else:
        return jsonify({"response": "I'm not sure how to respond to that."})

if __name__ == '__main__':
    print(f"{wishMe()}\nEVA is here for your service. What would you like to do today?")
    app.run(debug=True)