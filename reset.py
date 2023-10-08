import json
import os

import firebase_admin
from firebase_admin import credentials, db  # type: ignore

cred = credentials.Certificate(json.loads(os.environ['KEY']))

default_app = firebase_admin.initialize_app(  # type: ignore
    cred, {
        'databaseURL':
        'https://big-signifier-398111-default-rtdb.firebaseio.com/'
    })

print(db.reference('users').child('link_channel').get().val())