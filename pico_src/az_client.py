import json
from base64 import b64encode, b64decode
from hashlib import sha256
from time import time
from hmac import HMAC


NON_QUOTED = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' +\
             'abcdefghijklmnopqrstuvwxyz' +\
             '0123456789' +\
              '_.-~'


def quote(string, safe='/'):
    def quote_char(c):
        if c in NON_QUOTED+safe:
            return c
        else:
            return "%{:02X}".format(ord(c))
    quoted = [quote_char(c) for c in string]
    return ''.join(quoted)


def quote_plus(string):
    if ' ' not in string:
        return quote(string, '')
    space = ' '
    string = quote(string, space)
    return string.replace(' ', '+')


def urlencode(query):
    l = []
    for k, v in query.items():
        k = quote_plus(k)
        v = quote_plus(v)
        l.append(k + '=' + v)
    return '&'.join(l)


# Usage of SAS tokens documented here:
# https://learn.microsoft.com/en-us/azure/iot-hub/authenticate-authorize-sas?tabs=node
def generate_sas_token(uri, key, policy_name, expiry=3600):
    ttl = time() + expiry
    sign_key = "%s\n%d" % (quote_plus(uri), int(ttl))
    key = b64decode(key)
    hmac = HMAC(key, sign_key.encode('utf-8'), sha256).digest()
    signature = b64encode(hmac).decode()

    rawtoken = {
        'sr':  uri,
        'sig': signature,
        'se': str(int(ttl))
    }

    if policy_name is not None:
        rawtoken['skn'] = policy_name

    return 'SharedAccessSignature ' + urlencode(rawtoken)


def get_azure_config():
    class Config:
        def __init__(self, deviceid, hostname, username, password):
            self.deviceid = deviceid
            self.hostname = hostname
            self.username = username
            self.password = password

    with open("config/azure.json") as azure_config_file:
        azure_config = json.load(azure_config_file)

    hostname = azure_config['hostname']
    deviceid = azure_config['deviceid']
    primarykey = azure_config['primarykey']
    uri = f"{hostname}/{deviceid}"
    username = f"{uri}/?api-version=2021-04-12"
    password = generate_sas_token(uri, primarykey, '', 60*60*24)

    return Config(deviceid, hostname, username, password)
