import json
import os
import time
import firebase_admin
from firebase_admin import credentials, db  # type: ignore

cred = credentials.Certificate(json.loads(os.environ['KEY']))

app = firebase_admin.initialize_app(  # type: ignore
    cred, {
        'databaseURL':
        'https://big-signifier-398111-default-rtdb.firebaseio.com/'
    })

ref = db.reference('users/411435416/messages')
snapshot = ref.order_by_key().limit_to_last(1).get()
print(list(snapshot)[0])
print(db.reference(f'users/411435416/messages/{list(snapshot)[0]}/date').get())
print(time.time())
print(time.time() - 
      db.reference(f'users/411435416/messages/{list(snapshot)[0]}/date').get())