import json
import os

import firebase_admin
import telebot
from firebase_admin import credentials, db

cred = credentials.Certificate(json.loads(os.environ['KEY']))

default_app = firebase_admin.initialize_app(cred, {
    'databaseURL':
    'https://big-signifier-398111-default-rtdb.firebaseio.com/'
})

bot = telebot.TeleBot(os.environ['TOKEN'])


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
  bot.reply_to(
      message, """\
Hi there, I am EchoBot.
I am here to echo your kind words back to you. Just say anything nice and I'll say the 
exact same thing to you!\
""")


# Handle all other messages with content_type 'text' (content_types defaults to
# ['text'])
@bot.message_handler(func=lambda _message: True)
def echo_message(message):
  chat_test = -1001924397597
  bot.reply_to(message, message.text)
  if db.reference('/users_database/' + str(message.from_user.id)).get() is None:
      bot.create_forum_topic(chat_test,
      f'{message.from_user.first_name} {message.from_user.last_name}')
  db.reference('/users_database/' + str(message.from_user.id) + '/' +
               str(message.id)).set(message.json)


bot.infinity_polling()
