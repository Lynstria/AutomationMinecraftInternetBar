#!/usr/bin/env python3
"""
Upload.py - Nén thư mục versions Minecraft và tải lên Google Drive.
Repo: Lynstria/AutomationMinecraftInternetBar
"""

import os
import sys
import shutil
import zipfile
import time
import requests
from pathlib import Path
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

MINECRAFT_DIR = os.path.join(os.environ['APPDATA'], '.tlauncher', 'legacy', 'Minecraft', 'game')
VERSIONS_DIR = os.path.join(MINECRAFT_DIR, 'versions')
TEMP_ZIP = os.path.join(os.environ['TEMP'], 'versions.zip')

def zip_versions():
    if not os.path.exists(VERSIONS_DIR):
        raise FileNotFoundError(f"Không tìm thấy thư mục: {VERSIONS_DIR}")

    print(f"[*] Đang nén {VERSIONS_DIR} -> {TEMP_ZIP}")
    with zipfile.ZipFile(TEMP_ZIP, 'w', zipfile.ZIP_DEFLATED) as zf:
        base_path = Path(VERSIONS_DIR)
        for root, dirs, files in os.walk(VERSIONS_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, start=VERSIONS_DIR)
                # Cấu trúc: versions/... (giống khi giải nén sẽ ra thư mục versions)
                zf.write(full_path, arcname=os.path.join('versions', arcname))
            for d in dirs:
                dir_path = os.path.join(root, d)
                arc_dir = os.path.relpath(dir_path, start=VERSIONS_DIR)
                zf.write(dir_path, arcname=os.path.join('versions', arc_dir) + '/')

    print(f"[+] Đã tạo {TEMP_ZIP} ({os.path.getsize(TEMP_ZIP)} bytes)")

def upload_to_gdrive():
    gauth = GoogleAuth()
    # Sử dụng client_secrets.json có sẵn trong thư mục hiện tại
    if not os.path.exists('client_secrets.json'):
        print("[ERROR] Không tìm thấy client_secrets.json. Vui lòng đặt file vào cùng thư mục với Upload.py")
        sys.exit(1)
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    file_drive = drive.CreateFile({'title': 'versions.zip'})
    file_drive.SetContentFile(TEMP_ZIP)
    file_drive.Upload()
    print(f"[+] Đã tải lên Google Drive: {file_drive['title']} (ID: {file_drive['id']})")

    # Cấp quyền xem cho bất kỳ ai có link
    file_drive.InsertPermission({
        'type': 'anyone',
        'value': 'anyone',
        'role': 'reader'
    })
    share_link = f"https://drive.google.com/file/d/{file_drive['id']}/view?usp=sharing"
    print(f"[+] Link chia sẻ: {share_link}")

    # Gửi link qua Discord Webhook
    webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
    if webhook_url:
        requests.post(webhook_url, json={"content": f"📦 versions.zip đã sẵn sàng: {share_link}"})
        print("[+] Đã gửi link qua Discord.")
    else:
        print("[!] Không có Discord Webhook, không gửi thông báo.")

def cleanup():
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