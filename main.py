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


def id_topic_target(m):
  id_user = m.from_user.id
  if db.reference(f'/users/{id_user}').get() is None:
    first_name = m.from_user.first_name
    last_name = m.from_user.last_name
    topic = bot.create_forum_topic(
        chats_with_bot_id, f'{first_name} {last_name}',
        random.choice(
            [0x6FB9F0, 0xFFD67E, 0xCB86DB, 0x8EEE98, 0xFF93B2, 0xFB6F5F]))
    id_topic = topic.message_thread_id
    db.reference(f'/users/{id_user}/id_topic').set(id_topic)
  else:
    id_topic = db.reference(f'/users/{id_user}/id_topic').get(etag=True)[0]
  return id_topic


def send(m, text, markup, user_to):
  id_user = m.from_user.id
  id_topic = id_topic_target(m)
  bot.send_message(chats_with_bot_id, text, message_thread_id=id_topic)
  if user_to is True:
    bot.send_message(id_user, text, reply_markup=markup)
  db.reference(f'/users/{id_user}/{m.id}').set(m.json)
  db.reference(f'/users/{id_user}/{m.id}/answer_bot').set(text)


@bot.message_handler(func=lambda _message: True, chat_types=['private'])
def send_message(message):
  id_user = message.from_user.id
  send(message, f'@{message.from_user.username}\n{message.text}', 0, False)
  if db.reference(f'/users/{id_user}/link_channel').get() is None:
    send(message,
         db.reference('/script/start_text').get(),
         types.ForceReply(True, 'Ссылка на канал'), True)
    db.reference(f'/users/{id_user}/link_channel').set('wait')
  elif db.reference(f'/users/{id_user}/link_channel').get() == 'wait':
    if message.entities is not None:
      if message.entities[0].type == 'url':
        send(message, (
            'Отлично! Теперь отправьте мне ссылку на материал с канала, который'
            'вы хотели бы продвигать в первую очередь'), 0, True)
        offset = message.entities[0].offset
        length = message.entities[0].length
        db.reference(f'/users/{id_user}/link_channel').set(
            message.text[offset:offset + length])
        db.reference(f'/users/{id_user}/link_top_media').set('wait')
      else:
        send(message, 'Не вижу ссылки на канал в вашем сообщении',
             types.ForceReply(True, 'Ссылка на канал'), True)
    else:
      send(message, 'Ответ должен содержать ссылку на канал',
           types.ForceReply(True, 'Ссылка на канал'), True)


bot.infinity_polling()
