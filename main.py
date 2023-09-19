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
chat_test = int(os.environ['CHAT_TEST'])


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
  bot.reply_to(message, "Hi there, I am EchoBot")


@bot.message_handler(func=lambda _message: True)
def send_message(message):
  if db.reference('/users_database/' + str(message.from_user.id)).get() is None:
    topic = bot.create_forum_topic( chat_test,
        f'{message.from_user.first_name} {message.from_user.last_name}')
    id_topic = topic.message_thread_id
    db.reference('/users_database/' + str(message.from_user.id) +
                 '/topic_id').set(topic.message_thread_id)
  else:
    first_value = db.reference('/users_database/' + str(message.from_user.id) +
                 '/topic_id').get()
    id_topic = first_value
    print(id_topic)
  bot.send_message(chat_test, message.text, message_thread_id=id_topic)
  db.reference('/users_database/' + str(message.from_user.id) + '/' +
               str(message.id)).set(message.json)


# @bot.message_handler(content_types=['forum_topic_created'])
# def send_into_topic(message):
#   return message.id

bot.infinity_polling()
