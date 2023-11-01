import json
import os

import firebase_admin
from firebase_admin import credentials  # type: ignore

cred = credentials.Certificate(json.loads(os.environ['KEY']))

app = firebase_admin.initialize_app(  # type: ignore
    cred, {
        'databaseURL':
        'https://big-signifier-398111-default-rtdb.firebaseio.com/'
    })

text = "Класс! Вы зарегистрированы. Теперь посмотрим кому нужно помочь в первую очередь. Если всё же хотите ознакомиться с другими каналами, то нажмите на кнопки ниже."
text = text.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]').replace('(', '\\(').replace(')', '\\)').replace('~', '\\~').replace('"', '\"').replace('>', '\\>').replace('#', '\\#').replace('+', '\\+').replace('-', '\\-').replace('=', '\\=').replace('|', '\\|').replace('{', '\\{').replace('}','\\}').replace('.', '\\.').replace('!', '\\!')
print(text)