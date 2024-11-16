import random
import nltk
import spacy
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from collections import defaultdict
from bs4 import BeautifulSoup

# Initialize spaCy, transformers model, and TF-IDF classifier
nlp = spacy.load('en_core_web_sm')
qa_pipeline = pipeline("question-answering")  # Hugging Face pipeline for QA
vectorizer = TfidfVectorizer()
model = LogisticRegression()

# Sample intents and responses
intents = {
    "greetings": ["hello", "hi", "hey", "howdy"],
    "goodbye": ["bye", "goodbye", "see you", "later"],
    "ask_name": ["what's your name?", "who are you?", "your name?"],
    "small_talk": ["how are you?", "how's it going?", "how's everything?"],
    "joke": ["tell me a joke", "make me laugh", "joke"],
}

responses = {
    "greetings": ["Hello! How can I assist you today?", "Hi there! What can I do for you?", "Hey! How can I help you today?"],
    "goodbye": ["Goodbye! Have a great day!", "See you later!", "Take care!"],
    "ask_name": ["I am Theta, your AI chatbot!", "I'm Theta, here to help you with anything!"],
    "small_talk": ["I'm doing great, thank you for asking!", "I'm functioning well, thanks for asking!"],
    "joke": ["Why don't skeletons fight each other? They don't have the guts!", "Why was the math book sad? Because it had too many problems!"],
}

# Memory and Learning Mechanism
memory = defaultdict(list)
user_feedback = {}

# Function to fetch answers from the web when the bot doesn't understand
def fetch_from_web(query):
    search_url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    result = soup.find("h3")  # Looking for the first search result title

    if result:
        return result.text
    else:
        return "I couldn't find any relevant information on the web."

# Function to classify intent using a combination of models
def classify_intent(text):
    intents_labels = []
    all_phrases = []
    
    for intent, phrases in intents.items():
        for phrase in phrases:
            intents_labels.append(intent)
            all_phrases.append(phrase)
    
    if not model.coef_.any():  # Check if model is untrained
        X_train = vectorizer.fit_transform(all_phrases)
        model.fit(X_train, intents_labels)
    
    X_test = vectorizer.transform([text])
    prediction = model.predict(X_test)
    return prediction[0]

# Function to handle the '/start' command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! I am Theta, your personal AI chatbot. How can I assist you today?")

# Function to handle the '/help' command
def help_command(update: Update, context: CallbackContext):
    help_text = (
        "Here are some commands you can try:\n"
        "/start - Start a conversation with me.\n"
        "/help - Get help with commands.\n"
        "You can also ask me anything and I will try my best to respond!"
    )
    update.message.reply_text(help_text)

# Function to handle asking who created the bot
def created_by(update: Update, context: CallbackContext):
    update.message.reply_text("I was created by @lamarszn on Telegram.")

# Function to handle interactions
def chat_with_theta(update: Update, context: CallbackContext):
    user_input = update.message.text.lower()
    user_id = update.message.from_user.id

    # Check if the user has interacted with Theta before (memory)
    if user_id in memory:
        context_str = "You last asked me: " + " ".join(memory[user_id]) + "\n"
    else:
        context_str = "This is our first conversation!\n"

    # Classify the user's intent based on input
    intent = classify_intent(user_input)

    # Remember the user's message for future context
    memory[user_id].append(user_input)

    # Handle response based on the intent
    if intent in responses:
        response = random.choice(responses[intent])
    else:
        response = fetch_from_web(user_input)  # If the bot doesn't understand, fetch info from the web

    # Send the response with context
    update.message.reply_text(f"{context_str}Response: {response}")

# Main function to set up the bot
def main():
    # Your Telegram Bot token
    bot_token = '7708412147:AAHn53-AMuRbykqGQ__Lvro_mIlLuNbYgrM'

    # Set up the Updater and Dispatcher
    updater = Updater(bot_token, use_context=True)
    dispatcher = updater.dispatcher

    # Add handlers for commands and messages
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("created_by", created_by))  # Command to ask who made it
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, chat_with_theta))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main(
