import openai
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext

# Set up OpenAI API key (get your API key from OpenAI's website)
openai.api_key = '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'

# Function to handle the '/start' command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! I am Theta, your personal AI chatbot. How can I assist you today?")

# Function to interact with the AI model (OpenAI's GPT)
def chat_with_theta(update: Update, context: CallbackContext):
    user_input = update.message.text  # User's message
    
    # Get AI's response using OpenAI's GPT model
    try:
        response = openai.Completion.create(
            model="gpt-4",  # You can use other models if you prefer
            prompt=f"User: {user_input}\nTheta:",  # Chat context
            max_tokens=150,  # Control the length of the response
            temperature=0.7,  # Adjust creativity of the response
        )
        answer = response.choices[0].text.strip()  # Extract the response
        update.message.reply_text(answer)  # Send response to the user
    except Exception as e:
        update.message.reply_text("Sorry, I couldn't process your request right now.")
        print(f"Error: {e}")

# Function to handle unknown commands (to keep the bot polite)
def unknown(update: Update, context: CallbackContext):
    update.message.reply_text("Sorry, I don't understand that command. Try asking something else!")

# Main function to set up the bot
def main():
    # Your Telegram Bot token
    bot_token = '7624661998:AAGoC_dt767yi3rIGB9IDkmnWIyfFb0R95U'

    # Set up the Updater and Dispatcher
    updater = Updater(bot_token, use_context=True)
    dispatcher = updater.dispatcher

    # Add handlers for commands and messages
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, chat_with_theta))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
