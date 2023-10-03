import json
import os
import random
import threading

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
    topic = bot.create_forum_topic(
        chats_with_bot_id, f'{m.from_user.first_name} {m.from_user.last_name}',
        random.choice(
            [0x6FB9F0, 0xFFD67E, 0xCB86DB, 0x8EEE98, 0xFF93B2, 0xFB6F5F]))
    id_topic = topic.message_thread_id
    db.reference(f'/users/{id_user}/id_topic').set(id_topic)
    db.reference(f'/users/{id_user}/status').set('link_channel')
  else:
    id_topic = db.reference(f'/users/{id_user}/id_topic').get(etag=True)[0]
  return id_topic


def send(m, text, markup, user_to):
  id_user = m.from_user.id
  id_topic = id_topic_target(m)
  bot.send_message(chats_with_bot_id, text, message_thread_id=id_topic)
  if user_to is True:
    bot.send_message(id_user, text, reply_markup=markup)
  db.reference(f'/users/{id_user}/messages/{m.id}').set(m.json)
  db.reference(f'/users/{id_user}/messages/{m.id}/answer_bot').set(text)


def branch_which(m, branch, status, link, text_placeholder):
  id_user = m.from_user.id
  if m.entities is not None:
    if m.entities[0].type == 'url':
      send(m, db.reference(f'/script/{branch}/success').get(), 0, True)
      offset = m.entities[0].offset
      length = m.entities[0].length
      db.reference(f'/users/{id_user}/{link}').set(m.text[offset:offset +
                                                          length])
      db.reference(f'/users/{id_user}/status').set(status)
    else:
      send(m,
           db.reference(f'/script/{branch}/not_this_entities').get(),
           types.ForceReply(True, text_placeholder), True)
  else:
    send(m,
         db.reference(f'/script/{branch}/no_entities').get(),
         types.ForceReply(True, text_placeholder), True)


def bot_check():
  return bot.get_me()


def bot_runner():
  @bot.message_handler(func=lambda _message: True, chat_types=['private'])
  def send_message(message):
    id_user = message.from_user.id
    if id_user == int(os.environ['MY_ID']):
      send(message, f'Админка\n{message.text}', 0, False)
    else:
      send(message, f'@{message.from_user.username}\n{message.text}', 0, False)
    if db.reference(f'/users/{id_user}/status').get() == 'link_channel':
      send(message,
           db.reference('/script/start_text').get(),
           types.ForceReply(True, 'Ссылка на канал'), True)
      db.reference(f'/users/{id_user}/status').set('wait_link_channel')
    elif db.reference(f'/users/{id_user}/status').get(
    ) == 'wait_link_channel' or 'wait_link_top_media':
      if db.reference(f'/users/{id_user}/status').get() == 'wait_link_channel':
        branch_which(message, 'for_link_channel', 'wait_link_top_media',
                     'link_channel', 'Ссылка на канал')
      else:
        branch_which(message, 'for_link_top_media', 'registration_done',
                     'link_top_media', 'Ссылка на пост, видео или статью')
    else:
      send(message, 'красава ты прошёл регистрацию', 0, True)
  bot.infinity_polling(none_stop=True)


t = threading.Thread(target=bot_runner)
t.start()
