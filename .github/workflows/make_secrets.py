#! /usr/bin/python

import os
import json
from cryptography.fernet import Fernet


key = os.getenv('ENCRYPTION_KEY')
client_id = os.getenv('ONSHAPE_OAUTH_CLIENT_ID')
client_secret = os.getenv('ONSHAPE_OAUTH_SECRET')

fernet = Fernet(key)

json_data = json.dumps({'client_id': client_id, 'client_secret': client_secret})

with open('auth.json', 'wb') as file:
    file.write(fernet.encrypt(json_data.encode('utf-8')))
