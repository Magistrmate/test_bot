import json
import os
import random
import threading
import time

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
    db_set(m, 'score_help', '', '', 1)
    db_set(m, 'score_support', '', '', 1)
    db_set(m, 'score', '', '', 1)
  else:
    id_topic = db_get('users', m.from_user.id, 'id_topic')
  return id_topic


def create_buttons():
  create_markup = types.InlineKeyboardMarkup()
  button1 = types.InlineKeyboardButton('Поддержать этот канал ⬆ ❤',
                                       callback_data='support_channel')
  button2 = types.InlineKeyboardButton('⬅ Назад', callback_data='back')
  button3 = types.InlineKeyboardButton('Далее ➡', callback_data='next')
  button4 = types.InlineKeyboardButton('Рейтинговая таблица каналов 📊',
                                       callback_data='rate_channels')
  create_markup.row(button1)
  create_markup.row(button2, button3)
  create_markup.row(button4)
  return create_markup


def send(m, text, text_placeholder, user_to, addon, registraion, button):
  id_topic = id_topic_target(m)
  markup = None
  parse_mode = None
  if user_to:
    if check_hello(m.from_user.id):
      text = f'Здравствуйте, {m.from_user.first_name}, {text}'
    else:
      text = text.capitalize()
    if registraion:
      if addon == 'buttons':
        text = f'{text} \\(Пользуйтесь кнопками, пожалуйста\\)[?](https://dzen.ru/magistrmateworld)'
        markup = create_buttons()
        parse_mode = 'MarkdownV2'
      elif addon is None:
        markup = None
      else:
        markup = types.ForceReply(True, text_placeholder)
    else:
      
      text = f'{text} \\(Пользуйтесь кнопками, пожалуйста\\)[?](https://dzen.ru/magistrmateworld)'
      markup = create_buttons()
      parse_mode = 'MarkdownV2'

    bot.send_message(m.from_user.id,
                     text,
                     reply_markup=markup,
                     parse_mode=parse_mode)
    db_set(m, 'messages', m.id, '', m.json)
    db_set(m, 'messages', m.id, 'answer_bot', text)
  bot.send_message(chats_with_bot_id,
                   text,
                   reply_markup=markup,
                   message_thread_id=id_topic,
                   parse_mode=parse_mode)


def branch_which(m, branch, status, link, text_placeholder, button):
  if m.entities is not None:
    if m.entities[0].type == 'url':
      if 'dzen.ru' in m.text:
        send(m, db_get('script', branch, 'success'), text_placeholder, True,
             button, True,'')
        offset = m.entities[0].offset
        length = m.entities[0].length
        db_set(m, link, '', '', m.text[offset:offset + length])
        db_set(m, 'status', '', '', status)
      else:
        send(m, db_get('script', 'not_dzen_link', ''), text_placeholder, True,
             False, True,'')
    else:
      send(m, db_get('script', branch, 'not_this_entities'), text_placeholder,
           True, False, True,'')
  else:
    send(m, db_get('script', branch, 'no_entities'), text_placeholder, True,
         False, True,'')


def bot_check():
  return bot.get_me()


def check_admin(m):
  if m.from_user.id == int(os.environ['MY_ID']):
    username = 'Админ'
  else:
    username = f'@{m.from_user.username}'
  return username


def check_hello(id_user):
  try:
    last_message = list(db.reference(f'users/{id_user}/messages').order_by_key().\
       limit_to_last(1).get())[0]
    last_date = db.reference(
        f'users/{id_user}/messages/{last_message}/date').get()
    hello = time.time() - last_date >= 43200
  except TypeError:
    hello = True
  return hello


def bot_runner():

  @bot.message_handler(func=lambda _message: True, chat_types=['private'])
  def send_message(message):
    id_user = message.from_user.id
    send(message, f'{check_admin(message)}\n{message.text}', 0, False,
         'placeholder', True,'')
    if db_get('users', id_user,
              'status') != 'registration_done' and 'wait' not in db_get(
                  'users', id_user, 'status'):
      send(message, db_get('script', 'start_text', ''), 'Название канала',
           True, 'placeholder', True, '')
      db_set(message, 'status', '', '', 'wait_name_channel')
    elif 'wait' in db_get('users', id_user, 'status'):
      if db_get('users', id_user, 'status') == 'wait_name_channel':
        send(message, 'Хорошо, теперь сообщите мне вашу ссылку на канал',
             'Ссылка на канал', True, 'placeholder', True, '')
        db_set(message, 'status', '', '', 'wait_link_channel')
        db_set(message, 'name_channel', '', '', message.text)
      elif db_get('users', id_user, 'status') == 'wait_link_channel':
        branch_which(message, 'for_link_channel', 'wait_link_top_media',
                     'link_channel', 'Ссылка на канал', 'placeholder')
      else:
        branch_which(message, 'for_link_top_media', 'registration_done',
                     'link_top_media', 'Ссылка на пост, видео или статью',
                     'buttons')
    else:
      send(message, 'выберите, чтобы вы хотели посмотреть', 'Лучи добра', True,
           '', False, '')

  @bot.callback_query_handler(func=lambda _call: True)
  def callback_query_handler(call):
    send(call, f'*Нажал на кнопку {call.data}*', '', False, '', False, '')
    send(call, 'Далее епта', '', True, '', False, call.data)

  bot.infinity_polling(none_stop=True)


t = threading.Thread(target=bot_runner)
t.start()
