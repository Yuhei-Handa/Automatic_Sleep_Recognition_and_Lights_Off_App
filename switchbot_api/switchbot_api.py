import json
import time
import hashlib
import hmac
import base64
import uuid
import requests
from rich import print

class Bot:
    def __init__(self):
        bot_id = 'C93830325118'
        self.apiHeader = {}
        # open token
        token_path = 'credentials/token.txt'
        secret_path = 'credentials/secret.txt'

        # open token file
        with open(token_path, 'r') as file:
            token = file.read().replace('\n', '')

        # open secret file
        with open(secret_path, 'r') as file:
            secret = file.read().replace('\n', '')

        nonce = uuid.uuid4()
        t = int(round(time.time() * 1000))
        string_to_sign = '{}{}{}'.format(token, t, nonce)
        string_to_sign = bytes(string_to_sign, 'utf-8')
        secret = bytes(secret, 'utf-8')
        sign = base64.b64encode(hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest())

        #Build api header JSON
        self.apiHeader['Authorization']=token
        self.apiHeader['Content-Type']='application/json'
        self.apiHeader['charset']='utf8'
        self.apiHeader['t']=str(t)
        self.apiHeader['sign']=str(sign, 'utf-8')
        self.apiHeader['nonce']=str(nonce)

        self.bot_id = bot_id
        self.devices_url = f'https://api.switch-bot.com/v1.1/devices/{bot_id}/status'
        self.command = f'https://api.switch-bot.com/v1.1/devices/{bot_id}/commands'
        self.input_data = {
            'commandType': 'command',
            'command': 'press',
            'parameter': 'default'
        }

    def get_status(self):
        res = requests.get(self.devices_url, headers=self.apiHeader)
        data = res.json()
        power = data['body']['power']
        deviceMode = data['body']['deviceMode']
        return power, deviceMode

    def press(self):
        res = requests.post(self.command, headers=self.apiHeader, json=self.input_data)
        data = res.json()
        return data

    def switch(self):
        power, deviceMode = self.get_status()
        if power == 'on':
            self.input_data['command'] = 'turnOff'
        else:
            self.input_data['command'] = 'turnOn'
        res = requests.post(self.command, headers=self.apiHeader, json=self.input_data)
        data = res.json()
        return data
    
if __name__ == '__main__':
    device = Bot()
    print(device.press())
    print(device.switch())
    print(device.get_status())
