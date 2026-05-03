#!/usr/bin/env python3
"""
upload.py
- Nén thư mục versions Minecraft.
- Upload lên Google Drive vào thư mục Minecraft_Map, giữ lại file cũ (đổi tên).
"""

import os
import sys
import shutil
import zipfile
import datetime
import tempfile
from pathlib import Path
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

MINECRAFT_DIR = os.path.join(os.environ['APPDATA'], '.tlauncher', 'legacy', 'Minecraft', 'game')
VERSIONS_DIR = os.path.join(MINECRAFT_DIR, 'versions')
TEMP_ZIP = os.path.join(tempfile.gettempdir(), 'versions.zip')
DRIVE_FOLDER_NAME = 'Minecraft_Map'
FILE_NAME = 'versions.zip'

def zip_versions():
    if not os.path.exists(VERSIONS_DIR):
        raise FileNotFoundError(f"Không tìm thấy thư mục: {VERSIONS_DIR}")

    print(f"[*] Đang nén {VERSIONS_DIR} -> {TEMP_ZIP}")
    with zipfile.ZipFile(TEMP_ZIP, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(VERSIONS_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, start=VERSIONS_DIR)
                zf.write(full_path, arcname=os.path.join('versions', arcname))
            # Thư mục rỗng (optional)
            for d in _:
                dir_path = os.path.join(root, d)
                arc_dir = os.path.relpath(dir_path, start=VERSIONS_DIR)
                zf.write(dir_path, arcname=os.path.join('versions', arc_dir) + '/')
    print(f"[+] Đã tạo {TEMP_ZIP} ({os.path.getsize(TEMP_ZIP)} bytes)")

def upload_to_gdrive():
    credentials_path = os.environ.get('GOOGLE_CREDENTIALS_PATH')
    if not credentials_path or not os.path.exists(credentials_path):
        raise RuntimeError("Thiếu hoặc sai đường dẫn Google credentials.")

    gauth = GoogleAuth()
    gauth.LoadClientConfigFile(credentials_path)
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    # Tìm hoặc tạo thư mục Minecraft_Map
    folder_id = None
    query = f"title = '{DRIVE_FOLDER_NAME}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    file_list = drive.ListFile({'q': query}).GetList()
    if file_list:
        folder_id = file_list[0]['id']
        print(f"[*] Tìm thấy thư mục '{DRIVE_FOLDER_NAME}' (ID: {folder_id})")
    else:
        folder_metadata = {
            'title': DRIVE_FOLDER_NAME,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = drive.CreateFile(folder_metadata)
        folder.Upload()
        folder_id = folder['id']
        print(f"[+] Đã tạo thư mục '{DRIVE_FOLDER_NAME}' (ID: {folder_id})")

    # Tìm file versions.zip hiện có trong thư mục
    query = f"'{folder_id}' in parents and title = '{FILE_NAME}' and trashed = false"
    existing_files = drive.ListFile({'q': query}).GetList()
    old_file = existing_files[0] if existing_files else None

    # Nếu có file cũ, đổi tên nó thành versions_YYYYMMDD_HHMMSS.zip
    if old_file:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        new_title = f"versions_{timestamp}.zip"
        print(f"[*] Đổi tên file cũ '{old_file['title']}' -> '{new_title}'")
        old_file['title'] = new_title
        old_file.Upload()
        print(f"[+] Đã giữ lại phiên bản cũ với tên {new_title}")

    # Upload file mới
    file_drive = drive.CreateFile({'title': FILE_NAME, 'parents': [{'id': folder_id}]})
    file_drive.SetContentFile(TEMP_ZIP)
    file_drive.Upload()
    print(f"[+] Đã upload {FILE_NAME} (ID: {file_drive['id']})")

    # Gửi link qua Discord Webhook nếu có
    webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
    if webhook_url:
        share_link = f"https://drive.google.com/file/d/{file_drive['id']}/view?usp=sharing"
        requests.post(webhook_url, json={"content": f"📦 Phiên bản mới đã sẵn sàng: {share_link}"})
        print(f"[+] Đã gửi link qua Discord: {share_link}")

def cleanup():
    if os.path.exists(TEMP_ZIP):
        os.remove(TEMP_ZIP)

def main():
    print("=== Upload phiên bản Minecraft ===")
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