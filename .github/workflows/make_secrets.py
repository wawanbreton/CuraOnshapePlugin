#! /usr/bin/python

import os
import json


def xor_encrypt_decrypt(data, key):
    return ''.join(chr(ord(data[i]) ^ ord(key[i % len(key)])) for i in range(len(data)))

key = os.getenv('ENCRYPTION_KEY')
client_id = os.getenv('ONSHAPE_OAUTH_CLIENT_ID')
client_secret = os.getenv('ONSHAPE_OAUTH_SECRET')

json_data = json.dumps({'client_id': client_id, 'client_secret': client_secret})

with open('auth.json', 'wb') as file:
    json_data_encrypted = xor_encrypt_decrypt(json_data, key)
    file.write(json_data_encrypted.encode('utf-8'))
