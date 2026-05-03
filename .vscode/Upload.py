#!/usr/bin/env python3
"""
Upload.py - Nén thư mục versions Minecraft và tải lên Google Drive.
Yêu cầu: Biến môi trường DISCORD_WEBHOOK_URL, và file client_secrets.json trong thư mục làm việc.
"""

import os
import sys
import shutil
import zipfile
import time
import requests
from pathlib import Path

# Thư mục versions Minecraft
MINECRAFT_DIR = os.path.join(os.environ['APPDATA'], '.tlauncher', 'legacy', 'Minecraft', 'game')
VERSIONS_DIR = os.path.join(MINECRAFT_DIR, 'versions')

TEMP_ZIP = os.path.join(os.environ['TEMP'], 'versions.zip')

def zip_versions():
    """Nén thư mục versions với cấu trúc versions/ bên trong zip."""
    if not os.path.exists(VERSIONS_DIR):
        raise FileNotFoundError(f"Không tìm thấy thư mục: {VERSIONS_DIR}")

    print(f"[*] Đang nén {VERSIONS_DIR} -> {TEMP_ZIP}")
    with zipfile.ZipFile(TEMP_ZIP, 'w', zipfile.ZIP_DEFLATED) as zf:
        base_path = Path(VERSIONS_DIR)
        for root, dirs, files in os.walk(VERSIONS_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, start=VERSIONS_DIR)
                # Đảm bảo cấu trúc versions/... (không có thư mục cha phía trên)
                zf.write(full_path, arcname=os.path.join('versions', arcname))
            # Thêm thư mục rỗng nếu cần
            for d in dirs:
                dir_path = os.path.join(root, d)
                arc_dir = os.path.relpath(dir_path, start=VERSIONS_DIR)
                # Thêm entry thư mục (không bắt buộc nhưng giữ cấu trúc)
                zf.write(dir_path, arcname=os.path.join('versions', arc_dir) + '/')

    print(f"[+] Đã tạo {TEMP_Zip} ({os.path.getsize(TEMP_ZIP)} bytes)")

def upload_to_gdrive():
    """Tải file zip lên Google Drive sử dụng PyDrive2."""
    try:
        from pydrive2.auth import GoogleAuth
        from pydrive2.drive import GoogleDrive
    except ImportError:
        print("[ERROR] Chưa cài đặt PyDrive2. Dùng: pip install pydrive2")
        sys.exit(1)

    # Xác thực
    gauth = GoogleAuth()
    # Kiểm tra xem có file client_secrets.json không
    if not os.path.exists('client_secrets.json'):
        # Tạo file cấu hình mặc định nếu chưa có
        settings = {
            "client_config_backend": "file",
            "client_config_file": "client_secrets.json",
            "save_credentials": True,
            "save_credentials_backend": "file",
            "save_credentials_file": "credentials.json",
            "get_refresh_token": True,
            "oauth_scope": ["https://www.googleapis.com/auth/drive.file"]
        }
        with open('settings.yaml', 'w') as f:
            import yaml
            yaml.dump(settings, f)
        print("[!] Chưa có file client_secrets.json. Vui lòng tải từ Google Cloud Console và đặt vào thư mục hiện tại.")
        sys.exit(1)

    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    # Tạo file trên Drive
    file_drive = drive.CreateFile({'title': 'versions.zip'})
    file_drive.SetContentFile(TEMP_ZIP)
    file_drive.Upload()
    print(f"[+] Đã tải lên Google Drive: {file_drive['title']} (ID: {file_drive['id']})")

    # Gửi link qua Discord webhook (nếu có)
    webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
    if webhook_url:
        file_drive.InsertPermission({
            'type': 'anyone',
            'value': 'anyone',
            'role': 'reader'
        })
        share_link = file_drive['alternateLink']
        share_link = f"https://drive.google.com/file/d/{file_drive['id']}/view?usp=sharing"
        requests.post(webhook_url, json={"content": f"📦 versions.zip đã sẵn sàng: {share_link}"})
        print(f"[+] Link chia sẻ: {share_link}")

def cleanup():
    """Xóa file zip tạm."""
    if os.path.exists(TEMP_ZIP):
        os.remove(TEMP_ZIP)

def main():
    print("=== Upload.py - Nén và tải lên Google Drive ===")
    try:
        zip_versions()
        upload_to_gdrive()
        print("[✅] Hoàn tất.")
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    finally:
        cleanup()

if __name__ == "__main__":
    main()