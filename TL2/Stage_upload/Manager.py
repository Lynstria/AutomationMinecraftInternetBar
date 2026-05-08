#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manager.py - List Drive file revisions, write temp JSON, call Manager.ps1"""
import sys, os, json, tempfile, urllib.request, urllib.parse
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from oauth2_helper import get_access_token

CODE_TXT = os.path.join(os.path.dirname(__file__), '..', 'Code.txt')
TEMP_JSON = os.path.join(tempfile.gettempdir(), 'mc_versions.json')
DRIVE_FILE_ID = "1_JH04cXYbWSbhTmn3Y9jQFAf57DayWNM"

def load_credentials():
    with open(CODE_TXT, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_time(iso_str):
    """Convert '2026-05-08T10:30:00.000Z' to 'HH:mm-dd-MM_YYYY'."""
    try:
        dt = datetime.strptime(iso_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        return dt.strftime('%H:%M-%d-%m_%Y')
    except:
        return iso_str
def list_drive_revisions(creds):
    """List revisions of a Drive file, sorted newest first."""
    try:
        access_token = get_access_token(creds['refresh_token'], creds['client_id'], creds['client_secret'])
    except Exception as e:
        print("Loi lay access_token: {}".format(e))
        return [], None
    url = "https://www.googleapis.com/drive/v3/files/{}/revisions?fields=revisions(id,modifiedTime,size)".format(DRIVE_FILE_ID)
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read().decode('utf-8'))
    revisions = data.get('revisions', [])
    # Sort by modifiedTime descending (newest first)
    revisions.sort(key=lambda r: r.get('modifiedTime', ''), reverse=True)
    files = []
    for r in revisions:
        modified = r.get('modifiedTime', 'unknown')
        formatted = format_time(modified)
        size = r.get('size', '0')
        try:
            size_mb = int(size) / 1024 / 1024
            size_str = '{:.1f}MB'.format(size_mb)
        except:
            size_str = size
        files.append({
            'name': 'versions.zip (rev {})'.format(r.get('id', 'unknown')),
            'createdTime': formatted,
            'id': r.get('id'),
            'size': size_str
        })
    return files, access_token

def delete_revision(rev_id, creds):
    """Delete a revision by ID."""
    try:
        access_token = get_access_token(creds['refresh_token'], creds['client_id'], creds['client_secret'])
    except Exception as e:
        print("Loi lay access_token: {}".format(e))
        return False
    url = 'https://www.googleapis.com/drive/v3/files/{}/revisions/{}'.format(DRIVE_FILE_ID, rev_id)
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    req = urllib.request.Request(url, headers=headers, method='DELETE')
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        print("Loi xoa revision: {}".format(e))
        return False

def main():
    try:
        creds = load_credentials()
    except Exception as e:
        print("Loi doc Code.txt: {}".format(e))
        sys.exit(1)

    if len(sys.argv) > 1 and sys.argv[1] == '--delete':
        # Delete mode: sys.argv[2:] are revision IDs
        rev_ids = sys.argv[2:]
        deleted = []
        for rid in rev_ids:
            if delete_revision(rid, creds):
                deleted.append(rid)
                print("Da xoa: {}".format(rid))
        # Relist after deletion
        files, _ = list_drive_revisions(creds)
        with open(TEMP_JSON, 'w', encoding='utf-8') as f:
            json.dump(files, f, ensure_ascii=False, indent=2)
        print("Da cap nhat danh sach ({} revisions)".format(len(files)))
        sys.exit(0)

    files, _ = list_drive_revisions(creds)
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
