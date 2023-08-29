
import sqlite3
import threading
from telegram import Update
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv
import os
from omdb import OMDB

load_dotenv()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

Token = "6669992044:AAHUolqcLdT9pFKhsd-KKmga8-KhnXJ1Oi0"
Movie_api = "3587e463"

class MovieBot:
    def __init__(self, token, api_key):
        self.token = Token
        self.api_key = Movie_api
        self.updater = Updater(self.token)
        self.dispatcher = self.updater.dispatcher
        self.omdb_client = OMDB(self.api_key)


        self.connection = sqlite3.connect("search_history.db", check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS search_history "
                            "(user_id INTEGER, search_query TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
        self.connection.commit()

    def start(self, update: Update, context: CallbackContext) -> None:
        reply_buttons = [['/start', '/help'], ['/history']]
        reply_markup = ReplyKeyboardMarkup(reply_buttons, resize_keyboard=True)
        update.message.reply_text(
            "Hi! I am a movie bot. Send any movie name to get information about it.",
            reply_markup=reply_markup
        )

    def help_command(self, update: Update, context: CallbackContext) -> None:
        reply_buttons = [['/start', '/help'], ['/history']]
        reply_markup = ReplyKeyboardMarkup(reply_buttons, resize_keyboard=True)
        update.message.reply_text(
            "This is a movie rating bot. Just enter the movie name to get brief info.",
            reply_markup=reply_markup
        )

    def search(self, update: Update, context: CallbackContext):
        reply_buttons = [['/start', '/help'], ['/history']]
        reply_markup = ReplyKeyboardMarkup(reply_buttons, resize_keyboard=True)
        update.message.reply_text(
            "Please wait while I fetch the movie information...",
            reply_markup=None
        )

        user_id = update.message.from_user.id
        movie_name = update.message.text
        movie_info = self.omdb_client.movie_info(movie_name)

        message = ""

        if movie_info:
            threading.Thread(target=self._store_search_history, args=(user_id, movie_name)).start()

            rating_text = f"IMDb Rating: {movie_info['imdb_ratings']}\n"
            for rating in movie_info['ratings']:
                rating_text += f"{rating['Source']}: {rating['Value']}\n"

            youtube_trailer = movie_info.get("youtube_trailer", "Trailer link not available.")

            message = (f"{movie_info['title']} ({movie_info['year']}): \n\n" +
                       f"Plot:\n{movie_info['plot']}\n\n" +
                       f"Starring:\n{movie_info['actors']}\n\n" +
                       f"Ratings:\n{rating_text}" +
                       f"YouTube Trailer: {youtube_trailer}\n\n\n" +
                       f"Poster:\n{movie_info['poster']}\n\n"
                       )
        else:
            message = f"Movie '{movie_name}' not found on the OMDb site. Please check your spelling errors and try again."

        update.message.reply_text(text=message, reply_markup=None)

    def _store_search_history(self, user_id, movie_name):
        self.cursor.execute("INSERT INTO search_history (user_id, search_query) VALUES (?, ?)",
                            (user_id, movie_name))
        self.connection.commit()

    def view_search_history(self, update: Update, context: CallbackContext):
        user_id = update.message.from_user.id
        self.cursor.execute("SELECT search_query, timestamp FROM search_history WHERE user_id=?", (user_id,))
        search_history = self.cursor.fetchall()

        if search_history:
            message = "Your search history:\n"
            for query, timestamp in search_history:
                message += f"- {query} ({timestamp})\n"
        else:
            message = "Your search history is empty."

        update.message.reply_text(message)

    def error(self, update: Update, context: CallbackContext):
        logging.error(f"An error occurred: {context.error}")
        update.message.reply_text("An error occurred. Please try again later.")

    def run(self):
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("help", self.help_command))
        self.dispatcher.add_handler(CommandHandler("history", self.view_search_history))
        infor_handler = MessageHandler(Filters.text, self.search)
        self.dispatcher.add_handler(infor_handler)
        self.dispatcher.add_error_handler(self.error)

        self.updater.start_polling()
        self.updater.idle()

    def __del__(self):
        self.connection.close()

def main():
    token = Token
    api_key = Movie_api
    movie_bot = MovieBot(token, api_key)
    movie_bot.run()

if __name__ == '__main__':
    main()