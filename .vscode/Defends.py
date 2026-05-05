#!/usr/bin/env python3
"""
defends.py
- Sinh OTP tu day so 1-10: chon 4 so ngau nhien, dao tron roi gui qua Discord webhook moi 15 giay.
- Nguoi dung phai nhap dung ma hien tai de tiep tuc.
"""

import os
import sys
import time
import secrets
import requests
from config import load_config

# Fix encoding for Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Load config
try:
    _config = load_config()
except:
    _config = {}

# Day so nguon tu 1 den 10 dung de sinh OTP
DIGIT_POOL = "0123456789"

# OTP timeout tu config, mac dinh 15 giay
OTP_TIMEOUT = _config.get('otp_timeout_seconds', 15)

WEBHOOK_URL = None  # Will be set in main()


def generate_otp():
    """Chon 4 so ngau nhien tu DIGIT_POOL va dao tron bang cryptographically secure RNG."""
    chosen = secrets.SystemRandom().sample(DIGIT_POOL, 4)
    secrets.SystemRandom().shuffle(chosen)
    return ''.join(chosen)


def send_discord_message(content):
    data = {"content": content}
    try:
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        return response.status_code == 204
    except Exception as e:
        print(f"[!] Loi gui Discord: {e}")
        return False


def main():
    global WEBHOOK_URL
    WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
    if not WEBHOOK_URL:
        print("[ERROR] Thieu DISCORD_WEBHOOK_URL.")
        sys.exit(1)

    print("=== Xac thuc OTP ===")
    current_otp = generate_otp()
    last_otp_time = time.time()
    send_discord_message(f"🔐 Ma OTP cua ban ({OTP_TIMEOUT} giay): **{current_otp}**")
    print("[*] Ma OTP da duoc gui toi Discord.")

    while True:
        now = time.time()
        elapsed = now - last_otp_time

        # Neu qua OTP_TIMEOUT giay, tao ma moi va gui lai
        if elapsed >= OTP_TIMEOUT:
            current_otp = generate_otp()
            last_otp_time = now
            send_discord_message(f"🔄 Ma OTP moi ({OTP_TIMEOUT} giay): **{current_otp}**")
            print("[*] Ma OTP moi da duoc gui.")

        user_input = input("Nhap ma OTP (hoac Enter de cho): ").strip()
        if user_input == current_otp:
            print("[+] Xac thuc OTP thanh cong.")
            send_discord_message("✅ Nguoi dung da xac thuc OTP thanh cong.")
            sys.exit(0)
        elif user_input == "":
            continue
        else:
            print("[!] Ma OTP khong chinh xac.")
            send_discord_message("❌ Ai do da nhap sai ma OTP.")


if __name__ == "__main__":
    main()
