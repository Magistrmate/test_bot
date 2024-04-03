import json
import os
import random
import threading
import time
from random_unicode_emoji import random_emoji

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


def formating_text(text):
   text = (text.replace('_', '\\_').replace('*', '\\*').replace(
       '[', '\\[').replace(']', '\\]').replace('(', '\\(').replace(
           ')', '\\)').replace('~', '\\~').replace('"', '\"').replace(
               '>', '\\>').replace('#', '\\#').replace('+', '\\+').replace(
                   '-', '\\-').replace('=', '\\=').replace('|', '\\|').replace(
                       '{', '\\{').replace('}', '\\}').replace('.',
                                                               '\\.').replace(
                                                                   '!', '\\!'))
   return text


def db_get(name_db, key1, key2):
   return db.reference(f'/{name_db}/{key1}/{key2}').get(etag=True)[0]


def db_set(m, key1, key2, key3, value):
   return db.reference(f'/users/{m.from_user.id}/{key1}/{key2}/{key3}').set(
       value)


def id_topic_target(m):
   if db_get('users', m.from_user.id, '') is None:
      topic = bot.create_forum_topic(
          chats_with_bot_id,
          f'{m.from_user.first_name} {m.from_user.last_name}',
          random.choice(
              [0x6FB9F0, 0xFFD67E, 0xCB86DB, 0x8EEE98, 0xFF93B2, 0xFB6F5F]))
      id_topic = topic.message_thread_id
      db_set(m, 'id_topic', '', '', id_topic)
      db_set(m, 'status', '', '', '')
      db_set(m, 'score_help', '', '', 1)
      db_set(m, 'score_support', '', '', 1)
      db_set(m, 'rating', '', '', 1)
   else:
      id_topic = db_get('users', m.from_user.id, 'id_topic')
   return id_topic


def create_buttons(form, link, pin):
   create_markup = types.InlineKeyboardMarkup()
   if form == 'main':
      button1 = types.InlineKeyboardButton('⬆ Поддержать этот канал ❤',
                                           callback_data='support_channel')
      button2 = types.InlineKeyboardButton('⬅ Назад', callback_data='back')
      button3 = types.InlineKeyboardButton('Далее ➡', callback_data='next')
      button4 = types.InlineKeyboardButton('ТОП 10 каналов 📊',
                                           callback_data='rate_channels')
      create_markup.row(button1)
      create_markup.row(button2, button3)
      create_markup.row(button4)
   elif form == 'top':
      button1 = types.InlineKeyboardButton('Возврат ↩',
                                           callback_data='back_to_main')
      create_markup.row(button1)
   elif form == 'moder_question':
      button1 = types.InlineKeyboardButton(f'{link} Acceptance',
                                           callback_data='acceptance')
      button2 = types.InlineKeyboardButton(f'{pin} Rejection',
                                           callback_data='rejection')
      create_markup.row(button1, button2)

   else:
      button1 = types.InlineKeyboardButton('   Перейти оставить лайк 👍 и '\
                                           'комментарий 💬   ',  link)
      button2 = types.InlineKeyboardButton('Возврат ↩',
                                           callback_data='back_to_main')
      create_markup.row(button1)
      create_markup.row(button2)
   return create_markup


def message_channel(user_id):
   actual_page = db.reference(f'users/{user_id}/actual_page').get()
   quantity = len(db.reference('users').get())
   top_user_id = list(
       db.reference('users').order_by_child('rating').limit_to_last(
           actual_page).get())[0]
   name_channel = db.reference(f'users/{top_user_id}/name_channel').get()
   link_channel = db.reference(f'users/{top_user_id}/link_channel').get()
   rating = db.reference(f'users/{top_user_id}/rating').get()
   score_help = db.reference(f'users/{top_user_id}/score_help').get()
   score_support = db.reference(f'users/{top_user_id}/score_support').get()
   return formating_text(
       f'Статистика канала "{name_channel}":\n{score_support} 🫂 '
       f'(Очки поддержки)\n{score_help} 🙏 (Очки помощи)\n{rating} 🌟 (Рейтинг '
       f'(Очки поддержки/помощи))\n{actual_page} #️⃣ '
       f'в рейтинге из {quantity} каналов') + f'[\\.]({link_channel})'


def send(m, text, text_placeholder, user_to, status, markup, parse_mode=None):
   if user_to:
      if check_hello(m.from_user.id):
         text = f'Здравствуйте, {m.from_user.first_name}, {text}'
      if 'done' not in status:
         markup = types.ForceReply(True, text_placeholder)
      else:
         text = f'{formating_text(text)}\n{message_channel(m.from_user.id)}'
         markup = create_buttons('main', '', '')
         parse_mode = 'MarkdownV2'

      db_set(m, 'messages', m.id, '', m.json)
      db_set(m, 'messages', m.id, 'answer_bot', text)
      bot.send_message(m.from_user.id, text, parse_mode, reply_markup=markup)
   bot.send_message(chats_with_bot_id,
                    text,
                    parse_mode,
                    reply_markup=markup,
                    message_thread_id=id_topic_target(m))


def branch_which(m, branch, status, next_status, link, text_placeholder):
   if m.entities is not None:
      if m.entities[0].type == 'url':
         if 'dzen.ru' in m.text:
            send(m, db_get('script', branch, 'success'), text_placeholder,
                 True, next_status, None)
            offset = m.entities[0].offset
            length = m.entities[0].length
            db_set(m, link, '', '', m.text[offset:offset + length])
            db_set(m, 'status', '', '', next_status)
         else:
            send(m, db_get('script', 'not_dzen_link', ''), text_placeholder,
                 True, status, None)
      else:
         send(m, db_get('script', branch, 'not_this_entities'),
              text_placeholder, True, status, None)
   else:
      send(m, db_get('script', branch, 'no_entities'), text_placeholder, True,
           status, None)


def bot_check():
   return bot.get_me()


def check_admin(m):
   if m.from_user.id == int(os.environ['MY_ID']):
      username = 'Админ'
   elif m.from_user.username is None:
      username = m.from_user.first_name
   else:
      username = f'@{m.from_user.username}'
   return username


def check_hello(id_user):
   try:
      last_message = list(
          db.reference(f'users/{id_user}/messages').order_by_key().
          limit_to_last(1).get())[0]
      last_date = db.reference(
          f'users/{id_user}/messages/{last_message}/date').get()
      hello = time.time() - last_date >= 43200  # type: ignore
   except TypeError:
      hello = True
   return hello


def bot_runner():

   @bot.message_handler(func=lambda _message: True, chat_types=['private'])
   def send_message(message):
      id_user = message.from_user.id
      send(message, f'{check_admin(message)}\n{message.text}', '', False, '',
           None)
      status = db_get('users', id_user, 'status')
      if status == '':
         send(message, db_get('script', 'start_text', ''), 'Название канала',
              True, status, None)
         db_set(message, 'status', '', '', 'wait_name_channel')
      elif 'wait' in status:
         if status == 'wait_name_channel':
            send(message, 'Хорошо, теперь скиньте мне вашу ссылку на канал 😌',
                 'Ссылка на канал', True, status, None)
            db_set(message, 'status', '', '', 'wait_link_channel')
            db_set(message, 'name_channel', '', '', message.text)
         elif status == 'wait_link_channel':
            branch_which(message, 'for_link_channel', status,
                         'wait_link_top_media', 'link_channel',
                         'Ссылка на канал')
         elif status == 'wait_link_top_media':
            db_set(message, 'actual_page', '', '', 1)
            branch_which(message, 'for_link_top_media', status,
                         'registration_done', 'link_top_media',
                         'Ссылка на пост, видео или статью')
         else:
            send(message, 'Ожидаю скриншот с твоей помощью каналу 🙂',
                 'Нажми на скрепку и т.д.', True, status, None)
      else:
         send(message, 'выберите, кого бы вы хотели поддержать 🫂',
              'Лучи добра', True, status, None)

   @bot.callback_query_handler(
       func=lambda _call: _call.message.chat.type == 'private')
   def callback_query_handler(call, text=''):
      actual_page = db.reference(
          f'users/{call.from_user.id}/actual_page').get()
      markup = create_buttons('main', '', '')
      if call.data == 'next' or call.data == 'back' or call.data == 'back_to_main':
         quantity = len(db.reference('users').get())
         if call.data != 'back_to_main':
            if call.data == 'next':
               if actual_page == quantity:
                  actual_page = 1
               else:
                  actual_page = actual_page + 1  #type: ignore
            else:
               if actual_page == 1:
                  actual_page = quantity
               else:
                  actual_page = actual_page - 1  #type: ignore
            db_set(call, 'actual_page', '', '', actual_page)
         text = message_channel(call.from_user.id)
         markup = create_buttons('main', '', '')
      elif call.data == 'rate_channels':
         i = 1
         for user_id in list(
             reversed(db.reference('users').order_by_child('rating').get())):
            name_channel = db.reference(f'users/{user_id}/name_channel').get()
            link_channel = db.reference(f'users/{user_id}/link_channel').get()
            rating = db.reference(f'users/{user_id}/rating').get()
            score_help = db.reference(f'users/{user_id}/score_help').get()
            score_support = db.reference(
                f'users/{user_id}/score_support').get()
            text = text + formating_text(f'{i} #️⃣') + \
            f' [{name_channel}]({link_channel}) ' + \
            formating_text(f'{score_support} 🫂 {score_help} 🙏 {rating} 🌟\n')
            i = i + 1
         text = f'ТОП 10 каналов 📊\n{text}'
         markup = create_buttons('top', '', '')
      elif call.data == 'support_channel':
         actual_user_id = list(
             db.reference('users').order_by_child('rating').limit_to_last(
                 actual_page).get())[0]
         link_top_media = db.reference(
             f'users/{actual_user_id}/link_top_media').get()
         text = formating_text(db_get(
             'script', '', 'text_to_boost')) + f'[\\.]({link_top_media})'
         markup = create_buttons('top_media', link_top_media, '')
         db_set(call, 'status', '', '', 'wait_screenshot')
      send(call, f'{check_admin(call)}\n*Нажал на кнопку {call.data}*', '',
           False, '', None)
      send(call, text, '', False, '', markup)
      bot.edit_message_text(text,
                            call.message.chat.id,
                            call.message.id,
                            reply_markup=markup,
                            parse_mode='MarkdownV2')

   @bot.callback_query_handler(
       func=lambda _call: _call.message.chat.type == 'supergroup')
   def callback_query(call):
      if call.data == 'acceptance':
         bot.unpin_chat_message(call.message.chat.id, call.message.id)
         markup = create_buttons('moder_question', random_emoji()[0], '')
         id_to_user = list(db.reference('users').order_by_child('id_topic').equal_to(
                       call.message.message_thread_id).get())[0]
         bot.send_message(id_to_user, 'красава')
         score_support = db.reference(f'users/{id_to_user}/score_support').get()
         db.reference(f'users/{id_to_user}/score_support').set(score_support + 1) #type: ignore
         
      else:
         markup = create_buttons('moder_question', '', random_emoji()[0])
      bot.edit_message_reply_markup(call.message.chat.id,
                                    call.message.id,
                                    reply_markup=markup)

   @bot.message_handler(func=lambda _message: True, content_types=['photo'])
   def photo_handler(photo):
      db_set(photo, 'status', '', '', 'screenshot_done')
      sent = bot.send_photo(chats_with_bot_id,
                            photo.photo[-1].file_id,
                            f'{check_admin(photo)}\n{photo.caption}',
                            message_thread_id=id_topic_target(photo),
                            reply_markup=create_buttons(
                                'moder_question', '', ''))
      send(photo, db_get('script', '', 'after_help'), '', True,
           'registration_done', None)
      bot.pin_chat_message(chats_with_bot_id, sent.message_id)

   @bot.message_handler(content_types=['pinned_message'])
   def message_handler(notification):
      bot.delete_message(notification.chat.id, notification.message_id)

   bot.infinity_polling(none_stop=True)


t = threading.Thread(target=bot_runner)
t.start()
