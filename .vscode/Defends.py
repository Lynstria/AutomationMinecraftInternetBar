#!/usr/bin/env python3
"""
Defends.py - OTP động gửi qua Discord Webhook.
Repo: Lynstria/AutomationMinecraftInternetBar
"""

import os
import sys
import time
import random
import requests

# Mật khẩu gốc (dãy số sẽ bị hoán vị ngẫu nhiên)
SECRET = "147369852"  # <-- Thay bằng mật khẩu thực của bạn

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
if not WEBHOOK_URL:
    print("[ERROR] Chưa thiết lập biến môi trường DISCORD_WEBHOOK_URL.")
    sys.exit(1)

def generate_otp():
    digits = list(SECRET)
    random.shuffle(digits)
    return ''.join(digits)

def send_discord_message(content):
    data = {"content": content}
    try:
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        if response.status_code == 204:
            return True
        print(f"[!] Discord webhook trả về mã {response.status_code}: {response.text}")
        return False
    except Exception as e:
        print(f"[!] Lỗi gửi tin nhắn Discord: {e}")
        return False

def main():
    print("=== Defends.py - Xác thực OTP ===")
    print(f"Mật khẩu gốc có {len(SECRET)} chữ số.")
    
    otp = generate_otp()
    msg = f"🔐 Mã OTP của bạn (có hiệu lực 15 giây): **{otp}**"
    print("[*] Đang gửi OTP qua Discord...")
    if not send_discord_message(msg):
        print("[ERROR] Không thể gửi OTP. Kiểm tra lại webhook.")
        sys.exit(1)
    
    start_time = time.time()
    last_otp_time = start_time
    
    while True:
        elapsed = time.time() - start_time
        remaining = max(0, 120 - int(elapsed))  # Timeout 2 phút
        
        # Tạo OTP mới mỗi 15 giây
        if time.time() - last_otp_time >= 15:
            otp = generate_otp()
            msg = f"🔄 Mã OTP mới (15 giây): **{otp}**"
            print("[*] Gửi OTP mới...")
            send_discord_message(msg)
            last_otp_time = time.time()
        
        print(f"\r[*] Nhập mã OTP (còn {remaining}s): ", end='')
        user_input = input().strip()
        
        if user_input == otp:
            print("\n[+] Xác thực thành công!")
            send_discord_message("✅ Người dùng đã xác thực thành công.")
            sys.exit(0)
        elif user_input == "":
            continue
        else:
            print("[!] Mã OTP không chính xác.")
            send_discord_message("❌ Ai đó đã nhập sai mã OTP.")
            
        if time.time() - start_time > 120:
            print("\n[ERROR] Hết thời gian chờ.")
            send_discord_message("⏰ Hết thời gian xác thực (2 phút).")
            sys.exit(1)

if __name__ == "__main__":
    main()