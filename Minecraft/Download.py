#!/usr/bin/env python3
"""
Download.py (Repo: Lynstria/AutomationMinecraftInternetBar)
Tải TLauncher, GraalVM và versions từ Google Drive về thư mục Downloads của người dùng.
"""

import os
import sys
import time
import glob
import argparse
import base64
import gdown

DOWNLOAD_DIR = os.path.join(os.environ['USERPROFILE'], 'Downloads')
TLAUNCHER_URL = "https://dl1.tlauncher.org/f.php?f=files%2FTLauncher-Installer-1.9.5.1.exe"

# Headers giả lập trình duyệt để tránh 403
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

def download_file(url, dest_folder):
    os.makedirs(dest_folder, exist_ok=True)
    print(f"[Download] Đang tải: {url}")
    if "drive.google.com" in url:
        gdown.download(url, output=dest_folder, quiet=False, fuzzy=True)
    else:
        import requests
        local_filename = url.split('/')[-1].split('?')[0]
        file_path = os.path.join(dest_folder, local_filename)
        # Thêm headers vào request
        with requests.get(url, stream=True, allow_redirects=True, headers=HEADERS) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"[Download] Đã lưu: {file_path}")

def has_required_files():
    exe_files = glob.glob(os.path.join(DOWNLOAD_DIR, "*.exe"))
    zip_files = glob.glob(os.path.join(DOWNLOAD_DIR, "*.zip"))
    return len(exe_files) >= 1 and len(zip_files) >= 2

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--graalvm-url', required=True)
    parser.add_argument('--versions-url', required=True)
    args = parser.parse_args()

    print("=== Tải file ===")
    download_file(TLAUNCHER_URL, DOWNLOAD_DIR)
    download_file(args.graalvm_url, DOWNLOAD_DIR)
    download_file(args.versions_url, DOWNLOAD_DIR)
    time.sleep(2)

    if not has_required_files():
        print("[ERROR] Chưa đủ 3 file.")
        sys.exit(1)

    print("[+] Tải xong, gọi Work.py...")
    work_b64 = os.environ.get('WORK_PY_B64')
    if not work_b64:
        print("[ERROR] Không tìm thấy WORK_PY_B64")
        sys.exit(1)

    exec(base64.b64decode(work_b64).decode('utf-8'))

if __name__ == '__main__':
    main()
