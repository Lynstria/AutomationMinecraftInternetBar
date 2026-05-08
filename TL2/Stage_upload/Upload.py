#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Upload.py - Zip versions/ and update Drive file"""
import sys, os, json, zipfile, datetime, urllib.request, urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from oauth2_helper import get_access_token

CODE_TXT = os.path.join(os.path.dirname(__file__), '..', 'Code.txt')
MINECRAFT_DIR = os.path.join(os.environ.get('APPDATA', ''), '.minecraft')
VERSIONS_DIR = os.path.join(MINECRAFT_DIR, 'versions')
DRIVE_FILE_ID = '1_JH04cXYbWSbhTmn3Y9jQFAf57DayWNM'

def load_credentials():
    with open(CODE_TXT, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def zip_versions():
    if not os.path.isdir(VERSIONS_DIR):
        print("Khong tim thay {}".format(VERSIONS_DIR))
        return None
    zip_name = "versions.zip"
    zip_path = os.path.join(MINECRAFT_DIR, zip_name)
    print("Nen {} -> {} (store method)...".format(VERSIONS_DIR, zip_path))
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_STORED) as zf:
        for root, dirs, files in os.walk(VERSIONS_DIR):
            for fn in files:
                fp = os.path.join(root, fn)
                arcname = os.path.relpath(fp, os.path.dirname(VERSIONS_DIR))
                zf.write(fp, arcname)
    size = os.path.getsize(zip_path)
    print("Nen xong: {} ({} bytes)".format(zip_path, size))
    # Rename to dated version
    date_str = datetime.datetime.now().strftime("%d-%m-%Y")
    new_name = "versions-{}.zip".format(date_str)
    new_path = os.path.join(MINECRAFT_DIR, new_name)
    if os.path.exists(new_path):
        os.remove(new_path)
    os.rename(zip_path, new_path)
    print("Doi ten thanh: {}".format(new_path))
    return new_path

def upload_to_drive(zip_path, creds):
    try:
        access_token = get_access_token(creds['refresh_token'], creds['client_id'], creds['client_secret'])
    except Exception as e:
        print("Loi lay access_token: {}".format(e))
        return False

    url = 'https://www.googleapis.com/upload/drive/v3/files/{}?uploadType=media'.format(DRIVE_FILE_ID)
    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
        'Content-Type': 'application/zip'
    }

    print("Dang upload {} ({} bytes)...".format(zip_path, os.path.getsize(zip_path)))
    try:
        with open(zip_path, 'rb') as f:
            req = urllib.request.Request(url, data=f.read(), headers=headers, method='PATCH')
        resp = urllib.request.urlopen(req, timeout=300)
        result = json.loads(resp.read().decode('utf-8'))
        print("Upload thanh cong: {}".format(result.get('id')))
        return True
    except Exception as e:
        print("Loi upload: {}".format(e))
        return False

def main():
    zip_path = zip_versions()
    if not zip_path:
        sys.exit(1)
    try:
        creds = load_credentials()
    except Exception as e:
        print("Loi doc Code.txt: {}".format(e))
        sys.exit(1)
    if not upload_to_drive(zip_path, creds):
        sys.exit(1)
    print("Upload hoan thanh!")
    sys.exit(0)

if __name__ == '__main__':
    main()
