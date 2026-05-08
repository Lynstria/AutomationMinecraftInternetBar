#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Decode.py - AES256 decrypt nothing.enc, test Discord API, write Code.txt"""
import sys, os, json, urllib.request, urllib.error
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib_pure'))
from aes_pure import aes256_decrypt
from hashlib import sha256

NOTHING_ENC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nothing.enc')
CODE_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Code.txt')
MAX_ATTEMPTS = 4

def decrypt_nothing_enc(password):
    """Decrypt nothing.enc with password. Return dict or None."""
    try:
        with open(NOTHING_ENC, 'rb') as f:
            ciphertext = f.read()
        key = sha256(password.encode('utf-8')).digest()
        plaintext = aes256_decrypt(key, ciphertext)
        data = json.loads(plaintext.decode('utf-8'))
        return data
    except Exception:
        return None

def test_discord_api(url):
    """Test Discord webhook URL via GET request."""
    try:
        req = urllib.request.Request(url, method='GET', headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=5)
        return 200 <= resp.status < 400
    except Exception:
        return False

def main():
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            password = input("Nhập mã bảo mật: ").strip()
        except EOFError:
            print("No input")
            sys.exit(1)
        data = decrypt_nothing_enc(password)
        if data is None:
            print(f"Lần {attempt}/{MAX_ATTEMPTS}: Sai mã hoặc file lỗi")
            continue
        # Validate JSON fields (discord + OAuth2 fields)
        required = ['discord', 'refresh_token', 'client_id', 'client_secret']
        missing = [f for f in required if f not in data]
        if missing:
            print(f"Lần {attempt}/{MAX_ATTEMPTS}: JSON thiếu fields: {missing}")
            continue
        discord_url = data['discord']
        # Test Discord API
        if not test_discord_api(discord_url):
            print(f"Lần {attempt}/{MAX_ATTEMPTS}: API Discord không hợp lệ")
            continue
        # Write Code.txt
        with open(CODE_TXT, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        print("Giải mã thành công!")
        sys.exit(0)
    print("Hết số lần thử. Quay lại menu chính.")
    sys.exit(1)

if __name__ == '__main__':
    main()
