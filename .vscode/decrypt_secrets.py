#!/usr/bin/env python3
"""
decrypt_secrets.py
- Đọc secrets.enc từ thư mục hiện tại.
- Yêu cầu nhập mật khẩu (tối đa 3 lần). Nếu sai hiển thị "Sai mã API".
- Khi đúng thì giải mã và đặt biến môi trường DISCORD_WEBHOOK_URL, GOOGLE_CREDENTIALS_PATH.
"""

import os
import sys
import getpass
import tempfile
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

SALT = b"automatio_minecraft_salt_fixed"
MAX_ATTEMPTS = 3

def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def main():
    if not os.path.exists("secrets.enc"):
        print("[ERROR] Không tìm thấy file secrets.enc.")
        sys.exit(1)

    with open("secrets.enc", "rb") as f:
        encrypted_data = f.read()

    for attempt in range(1, MAX_ATTEMPTS + 1):
        password = getpass.getpass("🔑 Nhập mã bảo mật: ")
        try:
            key = derive_key(password, SALT)
            f = Fernet(key)
            decrypted = f.decrypt(encrypted_data).decode('utf-8')
        except Exception:
            print("❌ Sai mã API. Vui lòng thử lại.")
            if attempt == MAX_ATTEMPTS:
                print("Bạn đã nhập sai quá số lần cho phép.")
                sys.exit(1)
            continue

        parts = decrypted.split('\n', 1)
        if len(parts) != 2:
            print("[ERROR] Định dạng dữ liệu không hợp lệ.")
            sys.exit(1)

        discord_webhook = parts[0].strip()
        google_credentials = parts[1]

        # Đặt biến môi trường
        os.environ['DISCORD_WEBHOOK_URL'] = discord_webhook

        # Ghi Google credentials ra file tạm và trỏ biến
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
        tmp.write(google_credentials)
        tmp.close()
        os.environ['GOOGLE_CREDENTIALS_PATH'] = tmp.name

        print("[+] Xác thực thành công.")
        sys.exit(0)

if __name__ == "__main__":
    main()