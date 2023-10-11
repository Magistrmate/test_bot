import json
import os

import firebase_admin
from firebase_admin import credentials, db  # type: ignore

cred = credentials.Certificate(json.loads(os.environ['KEY']))

app = firebase_admin.initialize_app(  # type: ignore
    cred, {
        'databaseURL':
        'https://big-signifier-398111-default-rtdb.firebaseio.com/'
    })

list = []
for key in db.reference('users').get():
  name_channel = db.reference(f'users/{key}/name_channel').get()
  link_channel = db.reference(f'users/{key}/link_channel').get()
  list.append(name_channel + ':{')
  list.append(link_channel + '}')
  # print(db.reference(f'users/{key}/name_channel').get())
  # print(db.reference(f'users/{key}/link_channel').get())
print(list)
  