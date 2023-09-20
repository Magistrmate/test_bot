import json
import os
import random

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


@bot.message_handler(commands=['start'])
def send_welcome(message):
  bot.reply_to(message, "Hi there, I am EchoBot")


@bot.message_handler(func=lambda _message: True)
def send_message(message):
  id_user = str(message.from_user.id)
  first_name = message.from_user.first_name
  last_name = message.from_user.last_name
  if db.reference(f'/users/{id_user}').get() is None:
    icons = [0x6FB9F0, 0xFFD67E, 0xCB86DB, 0x8EEE98, 0xFF93B2, 0xFB6F5F]
    topic = bot.create_forum_topic(chat_test, f'{first_name} {last_name}',
                                   random.choice(icons))
    id_topic = topic.message_thread_id
    db.reference(f'/users/{id_user}/id_topic').set(id_topic)
  else:
    id_topic = db.reference(f'/users/{id_user}/id_topic/').get(etag=True)[0]
  bot.send_message(chat_test,
                   f'@{message.from_user.username}\n{message.text}',
                   message_thread_id=id_topic)
  db.reference(f'/users/{id_user}/{str(message.id)}').set(message.json)
  bot.send_message(id_user, 'Hello epta')
  bot.send_message(chat_test, 'Hello epta', message_thread_id=id_topic)


bot.infinity_polling()
