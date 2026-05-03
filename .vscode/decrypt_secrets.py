#!/usr/bin/env python3
"""
decrypt_secrets.py
- Đọc secrets.enc từ thư mục hiện tại.
- Yêu cầu nhập mật khẩu, giải mã và đặt biến môi trường.
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
        print("[ERROR] Không tìm thấy file secrets.enc trong thư mục hiện tại.")
        print("Hãy copy file secrets.enc (từ C:\\Download) vào thư mục chứa Main.ps1.")
        sys.exit(1)

    with open("secrets.enc", "rb") as f:
        encrypted_data = f.read()

    password = getpass.getpass("🔑 Nhập mật khẩu giải mã: ")

    try:
        key = derive_key(password, SALT)
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_data).decode('utf-8')
    except Exception:
        print("[ERROR] Sai mật khẩu hoặc dữ liệu hỏng.")
        sys.exit(1)

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

    print("[+] Secrets đã sẵn sàng cho phiên làm việc này.")

if __name__ == "__main__":
    main()