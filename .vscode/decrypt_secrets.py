#!/usr/bin/env python3
"""
decrypt_secrets.py
- Đọc secrets.enc từ thư mục hiện tại.
- Yêu cầu nhập mật khẩu (tối đa 3 lần). Nếu sai hiển thị "Sai mã API".
- In ra stdout DISCORD_WEBHOOK_URL và GOOGLE_CREDENTIALS_PATH để PowerShell đọc.
- Hỗ trợ cả định dạng cũ (fixed salt) và mới (random salt).
"""

import os
import sys
import getpass
import tempfile
import atexit
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

SALT_SIZE = 16
OLD_SALT = b"automatio_minecraft_salt_fixed"
MAX_ATTEMPTS = 3

# Biến toàn cục để theo dõi file tạm
_temp_file_path = None
_success = False

def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def cleanup_temp_file():
    """Dọn dẹp file tạm nếu script thoát không thành công."""
    global _temp_file_path
    if _temp_file_path and os.path.exists(_temp_file_path) and not _success:
        try:
            os.unlink(_temp_file_path)
            print(f"[!] Đã xóa file tạm: {_temp_file_path}")
        except:
            pass

def main():
    global _temp_file_path, _success

    if not os.path.exists("secrets.enc"):
        print("[ERROR] Không tìm thấy file secrets.enc.")
        sys.exit(1)

    with open("secrets.enc", "rb") as f:
        data = f.read()

    # Thử định dạng mới (có salt ngẫu nhiên ở đầu)
    # Nếu file đủ dài, 16 byte đầu là salt
    if len(data) > SALT_SIZE:
        salt = data[:SALT_SIZE]
        encrypted_data = data[SALT_SIZE:]
    else:
        # Định dạng cũ: dùng fixed salt
        salt = OLD_SALT
        encrypted_data = data

    for attempt in range(1, MAX_ATTEMPTS + 1):
        password = getpass.getpass("🔑 Nhập mã API: ")
        try:
            key = derive_key(password, salt)
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

        # Ghi Google credentials ra file tạm
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
        tmp.write(google_credentials)
        tmp.close()
        _temp_file_path = tmp.name

        # Đăng ký hàm dọn dẹp khi thoát
        atexit.register(cleanup_temp_file)

        # In ra stdout để PowerShell bắt
        print(f"DISCORD_WEBHOOK_URL={discord_webhook}")
        print(f"GOOGLE_CREDENTIALS_PATH={tmp.name}")
        print("[+] Xác thực thành công.")
        _success = True
        sys.exit(0)

if __name__ == "__main__":
    main()
