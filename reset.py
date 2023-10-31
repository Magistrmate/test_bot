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

actual = '5791523535'
keys = list(db.reference('users').get().keys())
for index, key in enumerate(db.reference('users').get()):
  if key == actual:
    print(index)
    back = keys[index - 1]
    print(back)
    next = keys[index + 1]
    print(next)
    print(index, db.reference(f'users/{key}/link_channel').get())