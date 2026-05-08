#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shield.py - Discord 4-digit code verification"""
import sys, os, json, urllib.request, random

CODE_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Code.txt')
MAX_ATTEMPTS = 4

def generate_code():
    """Generate 4-digit code and shuffle."""
    code = random.randint(0, 9999)
    code_str = f"{code:04d}"
    digits = list(code_str)
    random.shuffle(digits)
    shuffled = ''.join(digits)
    return code_str, shuffled

def send_discord_code(webhook_url, code_str):
    """Send code to Discord webhook."""
    msg = f"Mã xác thực: {code_str}"
    payload = json.dumps({"content": msg}).encode('utf-8')
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
        }
    )
    urllib.request.urlopen(req, timeout=10)

def shield():
    try:
        with open(CODE_TXT, 'r', encoding='utf-8') as f:
            creds = json.load(f)
        discord_url = creds['discord']
    except Exception as e:
        print(f"Lỗi đọc Code.txt: {e}")
        return False

    for attempt in range(1, MAX_ATTEMPTS + 1):
        code_str, shuffled = generate_code()
        try:
            send_discord_code(discord_url, shuffled)
            print(f"Đã gửi mã xác thực tới Discord ({attempt}/{MAX_ATTEMPTS})")
        except Exception as e:
            print(f"Lỗi gửi Discord ({attempt}/{MAX_ATTEMPTS}): {e}")

        try:
            user_input = input("Nhập mã xác thực (theo thứ tự hiển thị trên Discord): ").strip()
        except EOFError:
            print("No input")
            return False

        if user_input == shuffled:
            print("Xác thực thành công!")
            return True
        else:
            print(f"Mã sai ({attempt}/{MAX_ATTEMPTS})")

    print("Hết số lần thử. Quay lại menu chính.")
    return False

if __name__ == '__main__':
    sys.exit(0 if shield() else 1)
