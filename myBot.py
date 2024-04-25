import json
import os
import random
import threading
import time

import firebase_admin
import telebot
from firebase_admin import credentials, db  # type: ignore
from random_unicode_emoji import random_emoji
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
      db_set(m, 'support_channels_done', 1, '', 1)
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
      button5 = types.InlineKeyboardButton('Ваш канал 🌠',
                                           callback_data='self_channel')
      button6 = types.InlineKeyboardButton('Что к чему 💁‍♂',
                                           callback_data='help')

      create_markup.row(button1)
      create_markup.row(button2, button3)
      create_markup.row(button4)
      create_markup.row(button5, button6)
   elif form == 'top':
      if link == 'change_link':
         button1 = types.InlineKeyboardButton('Изменить ваш ТОП контент 🔄',
                                              callback_data='change_link')
         create_markup.row(button1)
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


def change_actual_page(a_p, q, n):
   a_p = a_p + n  #type: ignore
   if a_p > q:
      a_p = 1
   channel_page = list(
       db.reference('users').order_by_child('rating').limit_to_last(
       a_p).get())[0]
   return channel_page, a_p

   
def message_channel(c, from_to_back):
   actual_page = db_get('users', c.from_user.id, 'actual_page')
   quantity = len(db_get('users', '', ''))
   channel_page = list(
       db.reference('users').order_by_child('rating').limit_to_last(
           actual_page).get())[0]
   profile = dict.fromkeys([
       'name_channel', 'link_channel', 'rating', 'score_help', 'score_support',
       'link_top_media'
   ])
   list_support_channels_done = list(
       db_get('users', c.from_user.id, 'support_channels_done'))
   while c.from_user.id == int(channel_page):
      change_actual_page(actual_page, quantity, 1)
      if channel_page in list_support_channels_done:
         real_time = time.time() - db.reference(
             f'/users/{c.from_user.id}/support_channels_done/{channel_page}'
         ).get(etag=True)[0]
         if real_time >= 86400:
            db.reference(
                f'users/{c.from_user.id}/support_channels_done/{channel_page}'
            ).delete()
            db.reference(
                f'users/{c.from_user.id}/support_channels_done/1').set(1)
         change_actual_page(a_p, quantity, 2)
   while channel_page in list_support_channels_done:
      real_time = time.time() - db.reference(
          f'/users/{c.from_user.id}/support_channels_done/{channel_page}').get(
              etag=True)[0]
      if real_time >= 86400:
         db.reference(
             f'users/{c.from_user.id}/support_channels_done/{channel_page}'
         ).delete()
         db.reference(f'users/{c.from_user.id}/support_channels_done/1').set(1)
      change_actual_page(actual_page, quantity, 2)
      if c.from_user.id == int(channel_page):
         change_actual_page(actual_page, quantity, 1)
   for keys in profile:
      profile[keys] = db_get('users', channel_page, keys)
   text = (f'Статистика канала "{profile["name_channel"]}":\n'
           f'{profile["score_support"]} 🫂 (Очки поддержки)\n'
           f'{profile["score_help"]} 🙏 (Очки помощи)\n'
           f'{profile["rating"]} 🌟 (Рейтинг \n(Очки поддержки/помощи))\n'
           f'{actual_page} #️⃣ в рейтинге из {quantity} каналов')
   dot = f'[\\.]({profile["link_channel"]})'
   if from_to_back and c.data == 'self_channel':
      channel_page = c.from_user.id
      for keys in profile:
         profile[keys] = db_get('users', channel_page, keys)
      text = (f'Имя канала: {profile["name_channel"]}\n'
              f'Ссылка на ТОП контент: \n{profile["link_top_media"]}\n'
              f'Ссылка на канал: \n{profile["link_channel"]}\n'
              f'{profile["score_support"]} 🫂 (Очки поддержки)\n'
              f'{profile["score_help"]} 🙏 (Очки помощи)\n'
              f'{profile["rating"]} 🌟 (Рейтинг (Очки поддержки/помощи))\n'
              f'{actual_page} #️⃣ в рейтинге из {quantity} каналов')
      dot = ''
   db_set(c, 'actual_page', '', '', actual_page)
   return formating_text(text) + dot


def send(m, text, text_placeholder, user_to, status, markup, parse_mode=None):
   if user_to:
      if check_hello(m.from_user.id):
         text = f'Здравствуйте, {m.from_user.first_name}, {text}'
      if 'done' not in status:
         markup = types.ForceReply(True, text_placeholder)
      else:
         text = f'{formating_text(text)}\n{message_channel(m, False)}'
         markup = create_buttons('main', '', '')
         parse_mode = 'MarkdownV2'
      if 'Callback' not in str(m.__class__):
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
            if next_status == 'change_link_done':
               send(m, db_get('script', branch, 'change_link'),
                    text_placeholder, True, next_status, None)
            else:
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
         elif status == 'wait_link_top_media' or status == 'wait_change_link':
            if status == 'wait_link_top_media':
               db_set(message, 'actual_page', '', '', 1)
               next_status = 'registration_done'
            else:
               next_status = 'change_link_done'
            branch_which(message, 'for_link_top_media', status, next_status,
                         'link_top_media', 'Ссылка на пост, видео или статью')
            db_set(message, 'time_change_link', '', '', message.date)
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
      if call.data != 'change_link':
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
            text = message_channel(call, True)
            markup = create_buttons('main', '', '')
         elif call.data == 'rate_channels':
            i = 1
            for user_id in list(
                reversed(
                    db.reference('users').order_by_child('rating').get())):
               if int(user_id) == call.from_user.id:
                  name_channel = 'Ваш канал'
               else:
                  name_channel = db.reference(
                      f'users/{user_id}/name_channel').get()
               link_channel = db.reference(
                   f'users/{user_id}/link_channel').get()
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
            id_user_supporting = list(
                db.reference('users').order_by_child('link_channel').equal_to(
                    call.message.entities[0].url).get())[0]
            db_set(call, 'support_channel', '', '', id_user_supporting)
         elif call.data == 'self_channel':
            text = message_channel(call, True)
            markup = create_buttons('top', 'change_link', '')
         bot.edit_message_text(text,
                               call.message.chat.id,
                               call.message.id,
                               reply_markup=markup,
                               parse_mode='MarkdownV2')
         send(call, text, '', False, '', markup)
      else:
         if time.time() - db_get('users', call.from_user.id,
                                 'time_change_link') >= 86400:
            db_set(call, 'status', '', '', 'wait_change_link')
            send(call,
                 'жду от вас ссылку на новый контент с вашего канала 🙋‍♂',
                 'Ссылка на пост, видео или статью', True, 'wait_change_link',
                 None)
         else:
            time_wait = 86400 - (time.time() - db_get(
                'users', call.from_user.id, 'time_change_link'))
            bot.answer_callback_query(
                call.id, f'Извините, ссылку можно будет изменить через '
                f'{time.strftime("%H:%M:%S", time.gmtime(time_wait))} 🙏')
      send(call, f'{check_admin(call)}\n*Нажал на кнопку {call.data}*', '',
           False, '', None)

   @bot.callback_query_handler(
       func=lambda _call: _call.message.chat.type == 'supergroup')
   def callback_query(call):
      if call.data == 'acceptance':
         bot.unpin_chat_message(call.message.chat.id, call.message.id)
         markup = create_buttons('moder_question', random_emoji()[0], '')
         id_to_user = list(
             db.reference('users').order_by_child('id_topic').equal_to(
                 call.message.message_thread_id).get())[0]
         bot.send_message(id_to_user, 'красава')
         score_support = db.reference(
             f'users/{id_to_user}/score_support').get()
         db.reference(f'users/{id_to_user}/score_support').set(
             score_support + 1)  #type: ignore
         offset = call.message.caption_entities[0].offset
         length = call.message.caption_entities[0].length
         user_id_help = call.message.caption[offset:offset + length]
         bot.send_message(user_id_help, 'Тебе очко помощи 🙏')
         score_help = db.reference(f'users/{user_id_help}/score_help').get()
         db.reference(f'users/{user_id_help}/score_help').set(score_help +
                                                              1)  #type: ignore
      else:
         markup = create_buttons('moder_question', '', random_emoji()[0])
      bot.edit_message_reply_markup(call.message.chat.id,
                                    call.message.id,
                                    reply_markup=markup)

   @bot.message_handler(func=lambda _message: True, content_types=['photo'])
   def photo_handler(photo):
      db_set(photo, 'status', '', '', 'screenshot_done')
      support_channel = db_get('users', photo.from_user.id, 'support_channel')
      sent = bot.send_photo(
          chats_with_bot_id,
          photo.photo[-1].file_id,
          f'{check_admin(photo)}\n{photo.caption}\n||{support_channel}||',
          'MarkdownV2',
          message_thread_id=id_topic_target(photo),
          reply_markup=create_buttons('moder_question', '', ''))
      bot.pin_chat_message(chats_with_bot_id, sent.message_id)
      db_set(photo, 'support_channels_done', support_channel, '', time.time())
      db.reference(
          f'users/{photo.from_user.id}/support_channels_done/1').delete()
      send(photo, db_get('script', '', 'after_help'), '', True,
           'registration_done', None)

   @bot.message_handler(content_types=['pinned_message'])
   def message_handler(notification):
      bot.delete_message(notification.chat.id, notification.message_id)

   bot.infinity_polling(none_stop=True)


t = threading.Thread(target=bot_runner)
t.start()
