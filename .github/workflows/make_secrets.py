#! /usr/bin/python

import os
import json


def xor_encrypt_decrypt(data, key):
    return bytearray([data[i] ^ key[i % len(key)] for i in range(len(data))])

key = os.getenv('ENCRYPTION_KEY')
client_id = os.getenv('ONSHAPE_OAUTH_CLIENT_ID')
client_secret = os.getenv('ONSHAPE_OAUTH_SECRET')

json_data = json.dumps({'client_id': client_id, 'client_secret': client_secret})

with open('resources/auth.json', 'wb') as file:
    file.write(xor_encrypt_decrypt(json_data.encode('utf-8'), key.encode('utf-8')))
