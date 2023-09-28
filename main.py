import json
import os
import random

import firebase_admin
import telebot
from firebase_admin import credentials, db  # type: ignore
from telebot import types

cred = credentials.Certificate(json.loads(os.environ['KEY']))

default_app = firebase_admin.initialize_app(  # type: ignore
    cred, {
        'databaseURL':
        'https://big-signifier-398111-default-rtdb.firebaseio.com/'
    })

bot = telebot.TeleBot(os.environ['TOKEN'])
chats_with_bot_id = int(os.environ['CHATS_WITH_BOT_ID'])


def send(id_user, text, id_topic, markup):
  bot.send_message(chats_with_bot_id, text, message_thread_id=id_topic)
  if id_user != 0:
    bot.send_message(id_user, text, reply_markup=markup)


@bot.message_handler(func=lambda _message: True, chat_types=['private'])
def send_message(message):
  id_user = message.from_user.id
  first_name = message.from_user.first_name
  last_name = message.from_user.last_name
  if db.reference(f'/users/{id_user}').get() is None:
    topic = bot.create_forum_topic(
        chats_with_bot_id, f'{first_name} {last_name}',
        random.choice(
            [0x6FB9F0, 0xFFD67E, 0xCB86DB, 0x8EEE98, 0xFF93B2, 0xFB6F5F]))
    id_topic = topic.message_thread_id
    db.reference(f'/users/{id_user}/id_topic').set(id_topic)
  else:
    id_topic = db.reference(f'/users/{id_user}/id_topic').get(etag=True)[0]

  send(0, f'@{message.from_user.username}\n{message.text}', id_topic, 0)
  db.reference(f'/users/{id_user}/{message.id}').set(message.json)
  if db.reference(f'/users/{id_user}/link_channel').get() is None:
    send(id_user,
         db.reference('/script/start_text').get(), id_topic,
         types.ForceReply(input_field_placeholder='Ссылка на канал'))
    db.reference(f'/users/{id_user}/link_channel').set('wait')
  elif db.reference(f'/users/{id_user}/link_channel').get() == 'wait':
    if message.entities is not None:
      if message.entities[0].type == 'url':
        send(id_user, 'красава', id_topic,
             types.ForceReply(input_field_placeholder='Ссылка на канал'))
        offset = message.entities[0].offset
        length = message.entities[0].length
        db.reference(f'/users/{id_user}/link_channel').set(\
          message.text[offset:offset + length])
      else:
        send(id_user, 'ссылку оло', id_topic,
             types.ForceReply(input_field_placeholder='Ссылка на канал'))
    else:
      send(id_user, 'гони быстр', id_topic,
           types.ForceReply(input_field_placeholder='Ссылка на канал'))


bot.infinity_polling()
