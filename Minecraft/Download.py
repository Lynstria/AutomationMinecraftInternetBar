#!/usr/bin/env python3
"""
Download.py
Sử dụng thư viện gdown để tải file từ Google Drive về C:\download.
Sau đó gọi Work.py khi đã đủ file.
"""

import os, sys, time, glob, argparse, subprocess, base64
import gdown

DOWNLOAD_DIR = r"C:\download"
TLAUNCHER_URL = "https://dl1.tlauncher.org/f.php?f=files%2FTLauncher-Installer-1.9.5.1.exe"

def download_file(url, dest_folder):
    """Tải file từ URL (dùng gdown cho Google Drive links)."""
    os.makedirs(dest_folder, exist_ok=True)
    
    print(f"[Download] Đang tải: {url}")
    if "drive.google.com" in url:
        # Sử dụng gdown cho Google Drive
        gdown.download(url, output=dest_folder, quiet=False, fuzzy=True)
    else:
        # Fallback cho các URL thông thường (như TLauncher)
        import requests
        local_filename = url.split('/')[-1].split('?')[0]
        file_path = os.path.join(dest_folder, local_filename)
        with requests.get(url, stream=True, allow_redirects=True) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"[Download] Đã lưu: {file_path}")

def has_required_files():
    """Kiểm tra có ít nhất 1 file .exe và 2 file .zip trong thư mục download."""
    exe_files = glob.glob(os.path.join(DOWNLOAD_DIR, "*.exe"))
    zip_files = glob.glob(os.path.join(DOWNLOAD_DIR, "*.zip"))
    return len(exe_files) >= 1 and len(zip_files) >= 2

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--graalvm-url', required=True, help='Link Google Drive GraalVM')
    parser.add_argument('--versions-url', required=True, help='Link Google Drive Versions')
    args = parser.parse_args()

    print("=== Bắt đầu tải các file ===")
    # 1. Tải TLauncher
    download_file(TLAUNCHER_URL, DOWNLOAD_DIR)
    # 2. Tải 2 file zip từ Google Drive
    download_file(args.graalvm_url, DOWNLOAD_DIR)
    download_file(args.versions_url, DOWNLOAD_DIR)

    # Chờ một chút để chắc chắn file được ghi hoàn tất
    time.sleep(2)

    # Kiểm tra đủ 3 file
    if not has_required_files():
        print("[ERROR] Chưa đủ 3 file cần thiết (1 exe + 2 zip). Dừng pipeline.")
        sys.exit(1)

    print("Đã tải đủ 3 file. Chuẩn bị gọi Work.py...")
    # Lấy base64 của Work.py từ biến môi trường
    work_b64 = os.environ.get('WORK_PY_B64')
    if not work_b64:
        print("[ERROR] Không tìm thấy nội dung Work.py trong biến môi trường.")
        sys.exit(1)

    print("Thực thi Work.py trong RAM...")
    # Chạy Work.py bằng exec
    exec(base64.b64decode(work_b64).decode('utf-8'))

if __name__ == '__main__':
    main()