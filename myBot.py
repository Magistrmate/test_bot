import json
import os
import random
import threading

import firebase_admin
import telebot
from firebase_admin import credentials, db  # type: ignore
from telebot import types
from telebot.util import quick_markup

cred = credentials.Certificate(json.loads(os.environ['KEY']))

default_app = firebase_admin.initialize_app(  # type: ignore
    cred, {
        'databaseURL':
        'https://big-signifier-398111-default-rtdb.firebaseio.com/'
    })

bot = telebot.TeleBot(os.environ['TOKEN'])
chats_with_bot_id = int(os.environ['CHATS_WITH_BOT_ID'])


def db_get(name_db, key1, key2):
  return db.reference(f'/{name_db}/{key1}/{key2}').get(etag=True)[0]


def db_set(m, key1, key2, key3, value):
  return db.reference(f'/users/{m.from_user.id}/{key1}/{key2}/{key3}').set(
      value)


def id_topic_target(m):
  if db_get('users', m.from_user.id, '') is None:
    topic = bot.create_forum_topic(
        chats_with_bot_id, f'{m.from_user.first_name} {m.from_user.last_name}',
        random.choice(
            [0x6FB9F0, 0xFFD67E, 0xCB86DB, 0x8EEE98, 0xFF93B2, 0xFB6F5F]))
    id_topic = topic.message_thread_id
    db_set(m, 'id_topic', '', '', id_topic)
    db_set(m, 'status', '', '', 'link_channel')
  else:
    id_topic = db_get('users', m.from_user.id, 'id_topic')
  return id_topic


def send(m, text, text_placeholder, user_to, button):
  id_topic = id_topic_target(m)
  bot.send_message(chats_with_bot_id, text, message_thread_id=id_topic)
  if user_to:
    if button:
      markup = quick_markup({'hey': {
          'callback_data': 'whatever'
      }},
                            row_width=2)
    else:
      markup = types.ForceReply(True, text_placeholder)
    bot.send_message(m.from_user.id, text, reply_markup=markup)
    db_set(m, 'messages', m.id, '', m.json)
    db_set(m, 'messages', m.id, 'answer_bot', text)


def branch_which(m, branch, status, link, text_placeholder, button):
  if m.entities is not None:
    if m.entities[0].type == 'url':
      if 'dzen.ru' in m.text:
        send(m, db_get('script', branch, 'success'), text_placeholder, True,
             button)
        offset = m.entities[0].offset
        length = m.entities[0].length
        db_set(m, link, '', '', m.text[offset:offset + length])
        db_set(m, 'status', '', '', status)
      else:
        send(m, db_get('script', 'not_dzen_link', ''), text_placeholder, True,
             False)
    else:
      send(m, db_get('script', branch, 'not_this_entities'), text_placeholder,
           True, False)
  else:
    send(m, db_get('script', branch, 'no_entities'), text_placeholder, True,
         False)


def bot_check():
  return bot.get_me()


def check_admin(m):
  if m.from_user.id == int(os.environ['MY_ID']):
    username = 'Админ'
  else:
    username = f'@{m.from_user.username}'
  return username


def bot_runner():

  @bot.message_handler(func=lambda _message: True, chat_types=['private'])
  def send_message(message):
    id_user = message.from_user.id
    send(message, f'{check_admin(message)}\n{message.text}', 0, False, False)
    if db_get('users', id_user,
              'status') != 'registration_done' and 'wait' not in db_get(
                  'users', id_user, 'status'):
      send(message, db_get('script', 'start_text', ''), 'Название канала',
           True, False)
      db_set(message, 'status', '', '', 'wait_name_channel')
    elif 'wait' in db_get('users', id_user, 'status'):
      if db_get('users', id_user, 'status') == 'wait_name_channel':
        send(message, 'Хорошо, теперь сообщите мне вашу ссылку на канал',
             'Ссылка на канал', True, False)
        db_set(message, 'status', '', '', 'wait_link_channel')
        db_set(message, 'name_channel', '', '', message.text)
      elif db_get('users', id_user, 'status') == 'wait_link_channel':
        branch_which(message, 'for_link_channel', 'wait_link_top_media',
                     'link_channel', 'Ссылка на канал', False)
      else:
        branch_which(message, 'for_link_top_media', 'registration_done',
                     'link_top_media', 'Ссылка на пост, видео или статью',
                     True)
    else:
      send(message, 'красава ты прошёл регистрацию', 0, True, False)

  bot.infinity_polling(none_stop=True)


t = threading.Thread(target=bot_runner)
t.start()
