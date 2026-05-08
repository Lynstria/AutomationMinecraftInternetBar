#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manager.py - List Drive versions, write temp JSON, call Manager.ps1"""
import sys, os, json, tempfile, urllib.request, urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from oauth2_helper import get_access_token

CODE_TXT = os.path.join(os.path.dirname(__file__), '..', 'Code.txt')
TEMP_JSON = os.path.join(tempfile.gettempdir(), 'mc_versions.json')
FOLDER_ID = "1SJYI54NEQXb7a7OfZODSEO96rAUvPN12"

def load_credentials():
    with open(CODE_TXT, 'r', encoding='utf-8') as f:
        return json.load(f)

def list_drive_files(creds):
    """List files in Drive folder using refresh_token -> access_token."""
    try:
        access_token = get_access_token(creds['refresh_token'], creds['client_id'], creds['client_secret'])
    except Exception as e:
        print(f"Lỗi lấy access_token: {e}")
        return []
    url = f"https://www.googleapis.com/drive/v3/files?q='{FOLDER_ID}'+in+parents&fields=files(id,name,createdTime)"
    headers = {'Authorization': f'Bearer {access_token}'}
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read().decode('utf-8'))
    return data.get('files', [])

def main():
    try:
        creds = load_credentials()
    except Exception as e:
        print(f"Lỗi đọc Code.txt: {e}")
        sys.exit(1)

    files = list_drive_files(creds)
    with open(TEMP_JSON, 'w', encoding='utf-8') as f:
        json.dump(files, f, ensure_ascii=False, indent=2)
    print(f"Đã ghi danh sách {len(files)} file vào {TEMP_JSON}")

    # Call Manager.ps1
    manager_ps1 = os.path.join(os.path.dirname(__file__), '..', 'Manager.ps1')
    if not os.path.exists(manager_ps1):
        print(f"Không tìm thấy {manager_ps1}")
        sys.exit(1)

    ret = os.system(f'powershell.exe -File "{manager_ps1}" -JsonPath "{TEMP_JSON}"')
    sys.exit(ret)

if __name__ == '__main__':
    main()
