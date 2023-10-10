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

snapshot = db.reference('users').get()
for key in snapshot:
  move = db.reference(f'users/{key}/link_channel').get()
  print(move)