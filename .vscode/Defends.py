#!/usr/bin/env python3
"""
defends.py
- Gửi mã OTP (xáo trộn từ SECRET) qua Discord webhook mỗi 15 giây.
- Người dùng phải nhập đúng mã hiện tại để tiếp tục.
"""

import os
import sys
import time
import random
import requests

SECRET = "28042005"          # Thay bằng mật khẩu gốc của bạn
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

if not WEBHOOK_URL:
    print("[ERROR] Thiếu DISCORD_WEBHOOK_URL.")
    sys.exit(1)

def generate_otp():
    digits = list(SECRET)
    random.shuffle(digits)
    return ''.join(digits)

def send_discord_message(content):
    data = {"content": content}
    try:
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        return response.status_code == 204
    except Exception as e:
        print(f"[!] Lỗi gửi Discord: {e}")
        return False

def main():
    print("=== Xác thực OTP ===")
    current_otp = generate_otp()
    last_otp_time = time.time()
    send_discord_message(f"🔐 Mã OTP của bạn (15 giây): **{current_otp}**")
    print("[*] Mã OTP đã được gửi tới Discord.")

    while True:
        now = time.time()
        elapsed = now - last_otp_time

        # Nếu quá 15 giây, tạo mã mới và gửi lại
        if elapsed >= 15:
            current_otp = generate_otp()
            last_otp_time = now
            send_discord_message(f"🔄 Mã OTP mới (15 giây): **{current_otp}**")
            print("[*] Mã OTP mới đã được gửi.")

        user_input = input("Nhập mã OTP (hoặc Enter để chờ): ").strip()
        if user_input == current_otp:
            print("[+] Xác thực OTP thành công.")
            send_discord_message("✅ Người dùng đã xác thực OTP thành công.")
            sys.exit(0)
        elif user_input == "":
            continue
        else:
            print("[!] Mã OTP không chính xác.")
            send_discord_message("❌ Ai đó đã nhập sai mã OTP.")

if __name__ == "__main__":
    main()