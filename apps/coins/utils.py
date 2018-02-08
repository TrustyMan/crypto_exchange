import os
import hashlib
import hmac
import json
import requests
import subprocess

from bitcoin import *
from blockcypher import create_wallet_from_address
from cryptocurrency_wallet_generator import generate_wallet
from pywallet import wallet

from apps.authentication.models import Wallet, User
from apps.bitcoin_crypto.monero import *

CHANGELLY_API_URL = 'https://api.changelly.com'

CHANGELLY_API_KEY = os.environ.get('TWILIO_ACCOUNT_SID')
CHANGELLY_API_SECRET = os.environ.get('TWILIO_ACCOUNT_SID')
BLOCKCIPHER_API_KEY = os.environ.get('TWILIO_ACCOUNT_SID')


def changelly_transaction(method, params):
    message = {
                  "jsonrpc": "2.0",
                  "method": method,
                  "params": params,
                  "id": 1
                }

    serialized_data = json.dumps(message)

    sign = hmac.new(CHANGELLY_API_SECRET.encode('utf-8'), serialized_data.encode('utf-8'), hashlib.sha512).hexdigest()

    headers = {'api-key': CHANGELLY_API_KEY, 'sign': sign, 'Content-type': 'application/json'}
    response = requests.post(API_URL, headers=headers, data=serialized_data)

    return response.json()

def gen_address(user):
    priv = sha256(user.password)
    pub = privtopub(priv)
    addr = pubtoaddr(pub)
    return addr,pub,priv

def create_bitwallet(user):
    addr,pub,priv = gen_address(user)
    user.wallets.add(Wallet.objects.create(name='btc', address=addr, private=priv, public=pub))
    user.save()
    resp = create_wallet_from_address(wallet_name=user.username, address=addr, api_key=BLOCKCIPHER_API_KEY)
    if resp.get("addresses"):
        return resp.get("addresses")[0]

    else:
      return None

def create_litewallet(user):
    w = wallet.create_wallet(network="LTC", children=0)
    params = {
                "token": API_KEY_BLOCK,
                "name": user.username,
                "address": w["address"]
            }
    response = requests.post('https://api.blockcypher.com/v1/ltc/main/wallets',json=params)
    user.wallets.add(Wallet.objects.create(name='ltc', address=w["address"], private=w["private_key"]))
    user.save()
    return w["address"]

def create_ethwallet(user):
    private_key,address = generate_wallet("Ethereum")
    user.wallets.add(Wallet.objects.create(name='eth', address=address, private=private_key))
    user.save()
    return address

def create_xmrwallet(user):
    words,pub,private_key,address = gen_new_wallet()
    single_word = ",".join(word for word in words)
    user.wallets.add(Wallet.objects.create(name='xmr', address=address, public=pub, private=private_key, words=single_word))
    user.save()
    return address

def create_btgwallet(user):
    w = wallet.create_wallet(network="BTG", children=1)
    user.wallets.add(Wallet.objects.create(name='btg', address=w["address"], public=w["public_key"], private=w["private_key"]))
    user.save()
    return w["address"]

def create_bchwallet(user):
    w = wallet.create_wallet(network="BCH", children=1)
    user.wallets.add(Wallet.objects.create(name='bch', address=w["address"], public=w["public_key"], private=w["private_key"]))
    user.save()
    return w["address"]

def create_btc(address, amount):
    btc = User.objects.get(username="admin").wallets.get(name="btc")
    amt = amount*0.00000001
    transaction_id = simple_spend(from_privkey=btc.private, to_address=btc.address, to_satoshis=amt, coin_symbol='bcy')

