#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manager.py - List Drive file revisions, write temp JSON, call Manager.ps1"""
import sys, os, json, tempfile, urllib.request, urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from oauth2_helper import get_access_token

CODE_TXT = os.path.join(os.path.dirname(__file__), '..', 'Code.txt')
TEMP_JSON = os.path.join(tempfile.gettempdir(), 'mc_versions.json')
DRIVE_FILE_ID = "1_JH04cXYbWSbhTmn3Y9jQFAf57DayWNM"

def load_credentials():
    with open(CODE_TXT, 'r', encoding='utf-8') as f:
        return json.load(f)

def list_drive_revisions(creds):
    """List revisions of a Drive file."""
    try:
        access_token = get_access_token(creds['refresh_token'], creds['client_id'], creds['client_secret'])
    except Exception as e:
        print("Loi lay access_token: {}".format(e))
        return []
    url = "https://www.googleapis.com/drive/v3/files/{}/revisions?fields=revisions(id,modifiedTime,size)".format(DRIVE_FILE_ID)
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read().decode('utf-8'))
    revisions = data.get('revisions', [])
    # Map to same format as file list for Manager.ps1
    files = []
    for r in revisions:
        files.append({
            'name': 'versions.zip (rev {})'.format(r.get('id', 'unknown')),
            'createdTime': r.get('modifiedTime', 'unknown'),
            'id': r.get('id'),
            'size': r.get('size', 'unknown')
        })
    return files

def main():
    try:
        creds = load_credentials()
    except Exception as e:
        print("Loi doc Code.txt: {}".format(e))
        sys.exit(1)

    files = list_drive_revisions(creds)
    with open(TEMP_JSON, 'w', encoding='utf-8') as f:
        json.dump(files, f, ensure_ascii=False, indent=2)
    print("Da ghi danh sach {} revisions vao {}".format(len(files), TEMP_JSON))

    manager_ps1 = os.path.join(os.path.dirname(__file__), '..', 'Manager.ps1')
    if not os.path.exists(manager_ps1):
        print("Khong tim thay {}".format(manager_ps1))
        sys.exit(1)

    ret = os.system('powershell.exe -File "{}" -JsonPath "{}"'.format(manager_ps1, TEMP_JSON))
    sys.exit(ret)

if __name__ == '__main__':
    main()
