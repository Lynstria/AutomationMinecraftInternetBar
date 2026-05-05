#!/usr/bin/env python3
"""
upload.py
- Nén thư mục versions Minecraft.
- Upload lên Google Drive vào thư mục Minecraft_Map, giữ lại file cũ (đổi tên).
"""

import os
import sys
import zipfile
import datetime
import tempfile
import requests                     # <-- ĐÃ THÊM
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
# Try import, fallback to inlined code for irm | iex
try:
    from mc_utils import find_minecraft_dir
except ModuleNotFoundError:
    def find_minecraft_dir():
        import os
        import sys
        appdata_locations = set()
        for var in ["APPDATA", "LOCALAPPDATA"]:
            if var in os.environ:
                appdata_locations.add(os.environ[var])
        if "LOCALAPPDATA" in os.environ:
            appdata_locations.add(os.path.join(os.path.dirname(os.environ["LOCALAPPDATA"]), "LocalLow"))
        if "USERPROFILE" in os.environ:
            appdata_locations.add(os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming"))
            appdata_locations.add(os.path.join(os.environ["USERPROFILE"], "AppData", "Local"))
            appdata_locations.add(os.path.join(os.environ["USERPROFILE"], "AppData", "LocalLow"))
        if not appdata_locations:
            try:
                import getpass
                default = os.path.join("C:\\Users", getpass.getuser(), "AppData")
                appdata_locations.add(os.path.join(default, "Roaming"))
                appdata_locations.add(os.path.join(default, "Local"))
            except:
                pass
        candidates = []
        for base in appdata_locations:
            if not os.path.exists(base):
                continue
            for d in os.listdir(base):
                full = os.path.join(base, d)
                if d.lower() == ".tlauncher" and os.path.isdir(full):
                    for root, dirs, files in os.walk(full):
                        for subd in dirs:
                            if subd.lower() == "game":
                                game_dir = os.path.join(root, subd)
                                if os.path.exists(game_dir):
                                    candidates.append(game_dir)
                    mc_game = os.path.join(full, "Minecraft", "game")
                    if os.path.exists(mc_game):
                        candidates.append(mc_game)
                if d.lower() == ".minecraft" and os.path.isdir(full):
                    candidates.append(full)
                    break
        if not candidates:
            tried = "\n".join(str(p) for p in appdata_locations)
            raise FileNotFoundError(f"Khong tim thay thu muc Minecraft trong AppData.\nDa thu cac vi tri:\n{tried}")
        return candidates[0]

TEMP_ZIP = os.path.join(tempfile.gettempdir(), 'versions.zip')
DRIVE_FOLDER_NAME = 'Minecraft_Map'
FILE_NAME = 'versions.zip'

def get_versions_dir():
    """Trả về đường dẫn thư mục versions thực tế."""
    minecraft_dir = find_minecraft_dir()
    versions_dir = os.path.join(minecraft_dir, 'versions')
    if os.path.exists(versions_dir):
        return versions_dir
    raise FileNotFoundError(f"Không tìm thấy thư mục versions trong {minecraft_dir}")

def zip_versions():
    versions_dir = get_versions_dir()
    print(f"[*] Đang nén {versions_dir} -> {TEMP_ZIP}")
    with zipfile.ZipFile(TEMP_ZIP, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(versions_dir):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, start=versions_dir)
                zf.write(full_path, arcname=os.path.join('versions', arcname))
            for d in dirs:                              # <-- SỬA: dùng dirs thay vì _
                dir_path = os.path.join(root, d)
                arc_dir = os.path.relpath(dir_path, start=versions_dir)
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

    # Tìm file versions.zip hiện có
    query = f"'{folder_id}' in parents and title = '{FILE_NAME}' and trashed = false"
    existing_files = drive.ListFile({'q': query}).GetList()
    old_file = existing_files[0] if existing_files else None

    if old_file:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        new_title = f"versions_{timestamp}.zip"
        print(f"[*] Đổi tên file cũ '{old_file['title']}' -> '{new_title}'")
        old_file['title'] = new_title
        old_file.Upload()
        print(f"[+] Đã giữ lại phiên bản cũ với tên {new_title}")

    file_drive = drive.CreateFile({'title': FILE_NAME, 'parents': [{'id': folder_id}]})
    file_drive.SetContentFile(TEMP_ZIP)
    file_drive.Upload()

    # Cấp quyền công khai (anyone with link can view)
    file_drive.InsertPermission({
        'type': 'anyone',
        'role': 'reader',
        'withLink': True
    })
    file_id = file_drive['id']
    print(f"[+] Đã upload {FILE_NAME} (ID: {file_id}) và cấp quyền công khai")

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
