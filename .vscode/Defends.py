#!/usr/bin/env python3
"""
defends.py
- Gửi mã OTP (xáo trộn từ SECRET) qua Discord webhook mỗi 15 giây.
- Người dùng phải nhập đúng mã hiện tại để tiếp tục.
"""

import os
import sys
import time
import secrets
import requests

# Đọc SECRET từ biến môi trường OTP_SECRET
# Nếu không có, yêu cầu người dùng nhập (chỉ lần đầu, các lần sau nên set env)
SECRET = os.environ.get("246810")
if not SECRET:
    # Nếu chạy từ Main.ps1, SECRET nên được set từ trước
    # Ở đây dùng input để tương thích ngược
    try:
        SECRET = input("Nhập SECRET cho OTP: ").strip()
    except:
        pass
    if not SECRET:
        print("[ERROR] Thiếu OTP_SECRET. Hãy set biến môi trường OTP_SECRET trước khi chạy.")
        sys.exit(1)

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

if not WEBHOOK_URL:
    print("[ERROR] Thiếu DISCORD_WEBHOOK_URL.")
    sys.exit(1)

def generate_otp():
    """Tạo OTP bằng cách xáo trộn SECRET sử dụng cryptographically secure RNG."""
    digits = list(SECRET)
    secrets.SystemRandom().shuffle(digits)
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