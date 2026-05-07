#!/usr/bin/env python3
"""Upload.py - Zip versions/ and upload to Drive"""
import sys, os, json, zipfile, datetime, urllib.request, urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from oauth2_helper import get_access_token

CODE_TXT = os.path.join(os.path.dirname(__file__), '..', 'Code.txt')
VERSIONS_DIR = os.path.join(os.environ.get('APPDATA', ''), '.minecraft', 'versions')
DRIVE_FOLDER_ID = '1SJYI54NEQXb7a7OfZODSEO96rAUvPN12'

def load_credentials():
    with open(CODE_TXT, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data  # dict with discord, refresh_token, client_id, client_secret

def zip_versions():
    if not os.path.isdir(VERSIONS_DIR):
        print(f"Khong tim thay {VERSIONS_DIR}")
        return None
    date_str = datetime.datetime.now().strftime("%d-%m-%Y")
    zip_name = f"versions-{date_str}.zip"
    zip_path = os.path.join(os.environ.get('TEMP', '.'), zip_name)
    print(f"Nen {VERSIONS_DIR} -> {zip_path} (store method)...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_STORED) as zf:
        for root, dirs, files in os.walk(VERSIONS_DIR):
            for file in files:
                fp = os.path.join(root, file)
                arcname = os.path.relpath(fp, os.path.dirname(VERSIONS_DIR))
                zf.write(fp, arcname)
    print(f"Nen xong: {zip_path}")
    return zip_path

def upload_to_drive(zip_path, creds):
    """Upload zip to Drive folder using refresh_token -> access_token."""
    try:
        access_token = get_access_token(creds['refresh_token'], creds['client_id'], creds['client_secret'])
    except Exception as e:
        print(f"Loi lay access_token: {e}")
        return False

    # Upload via Drive API (simple upload)
    url = 'https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart'
    boundary = '---python-upload-boundary'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': f'multipart/related; boundary={boundary}'
    }

    # Metadata
    metadata = json.dumps({
        'name': os.path.basename(zip_path),
        'parents': [DRIVE_FOLDER_ID]
    })

    # Build multipart body
    body_parts = []
    body_parts.append(f'--{boundary}')
    body_parts.append('Content-Type: application/json; charset=UTF-8')
    body_parts.append('')
    body_parts.append(metadata)
    body_parts.append(f'--{boundary}')
    body_parts.append('Content-Type: application/zip')
    body_parts.append('')
    body = '\r\n'.join(body_parts).encode('utf-8')
    with open(zip_path, 'rb') as f:
        body += f.read()
    body += f'\r\n--{boundary}--\r\n'.encode('utf-8')

    try:
        req = urllib.request.Request(url, data=body, headers=headers)
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read().decode('utf-8'))
        print(f"Upload thanh cong: {result.get('id')}")
        return True
    except Exception as e:
        print(f"Loi upload: {e}")
        return False

def main():
    zip_path = zip_versions()
    if not zip_path:
        sys.exit(1)
    try:
        creds = load_credentials()
    except Exception as e:
        print(f"Loi doc Code.txt: {e}")
        sys.exit(1)
    if not upload_to_drive(zip_path, creds):
        sys.exit(1)
    print("Upload hoan thanh!")
    sys.exit(0)

if __name__ == '__main__':
    main()
