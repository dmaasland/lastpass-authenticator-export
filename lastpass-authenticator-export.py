#!/usr/bin/env python3

import requests
import binascii
import hashlib
import base64
import json
import os
import pyotp
import qrcode
import argparse
import getpass

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

VERIFY = True
USER_AGENT = 'lastpass-python/{}'.format('0.3.2')
CLIENT_ID = 'LastPassAuthExport'

def iterations(username):

    url = 'https://lastpass.com/iterations.php'
    params = {
        'email': username
    }
    headers = {
        'user-agent': USER_AGENT
    }

    r = requests.get(
        url = url,
        params = params,
        verify = VERIFY,
        headers = headers
    )

    try:
        iterations = int(r.text)
    except ValueError:
        iterations = 5000
        
    return iterations


def create_hash(username, password, iteration_count):
    
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), username.encode('utf-8'), iteration_count, 32)
    
    login_hash = binascii.hexlify(
        hashlib.pbkdf2_hmac('sha256', key, password.encode('utf-8'), 1, 32)
    )

    return key, login_hash


def login(username, password, otp=None):

    session = requests.Session()
    session.headers = {'user-agent': USER_AGENT}
    url = 'https://lastpass.com/login.php'
    iteration_count = iterations(username)
    key, login_hash = create_hash(username, password, iteration_count)

    data = {
        'method': 'mobile',
        'web': 1,
        'xml': 1,
        'username': username,
        'hash': login_hash,
        'iterations': iteration_count,
        'imei': CLIENT_ID
    }

    if otp:
        data.update({'otp': otp})

    r = session.post(
        url = url,
        data = data,
        verify = VERIFY
    )

    if not r.text.startswith('<ok'):
        print('Login failed!')
        print(r.text)
        exit(1)
    else:
        csrf = session.post('https://lastpass.com/getCSRFToken.php', verify=VERIFY).text
        return r.cookies.get_dict()['PHPSESSID'], csrf, key



def get_mfa_backup(session, csrf):

    url = 'https://lastpass.com/lmiapi/authenticator/backup'

    headers = {
        'X-CSRF-TOKEN': csrf,
        'X-SESSION-ID': session,
        'user-agent': USER_AGENT
    }

    r = requests.get(
        url = url,
        headers = headers,
        verify = VERIFY
    )

    return r.json()['userData']


def decrypt_user_data(user_data, key):

    data_parts = user_data.split('|')
    iv = base64.b64decode(data_parts[0].split('!')[1])
    ciphertext = base64.b64decode(data_parts[1])

    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    plaintext = unpad(
        cipher.decrypt(ciphertext),
        AES.block_size
    )
    mfa_data = json.loads(plaintext)
    
    return mfa_data


def write_out(mfa_data):

    if not os.path.isdir('export'):
        os.makedirs('export')

    with open('export/export.json', 'w') as f:
        f.write(json.dumps(mfa_data))

    table = "<table>\n"
    table += "  <tr>\n"
    table += "    <th>Issuer</th>\n"
    table += "    <th>Account</th>\n"
    table += "    <th>QR</th>\n"
    table += "  </tr>\n"


    for account in mfa_data['accounts']:
        totp = pyotp.TOTP(account['secret'].replace(' ', ''))

        uri = totp.provisioning_uri(
            name = account['userName'],
            issuer_name = account['issuerName']
        )

        img = qrcode.make(uri)
        img.save(f'export/{account["accountID"]}.png')

        table += "  <tr>\n"
        table += f"    <td>{account['issuerName']}</td>\n"
        table += f"    <td>{account['userName']}</td>\n"
        table += f"    <td><img src='{account['accountID']}.png' width='200' height='200'></td>\n"
        table += f"  </tr>\n"

    table += "</table>"

    with open('export/export.html', 'w') as f:
        f.write(table)


def get_args():
    parser = argparse.ArgumentParser(description='Export LastPass authenticator QR Codes.')
    parser.add_argument('-u', '--username', help='LastPass username', required=True)
    parser.add_argument('-o', '--otp', help='LastPass OTP', required=False)

    return parser.parse_args()


def main():

    args = get_args()
    username = args.username
    otp = args.otp
    password = getpass.getpass()

    session, csrf, key = login(username, password, otp)
    user_data = get_mfa_backup(session, csrf)
    mfa_data = decrypt_user_data(user_data, key)
    write_out(mfa_data)


if __name__ == '__main__':
    main()
