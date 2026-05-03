#!/usr/bin/env python3
"""
Work.py (Repo: Lynstria/AutomationMinecraftInternetBar)
- Quét thư mục download, chạy TLauncher installer.
- Theo dõi tiến trình Java + TLauncher.
- Giải nén, di chuyển version và Java.
"""

import os
import sys
import glob
import time
import shutil
import zipfile
import subprocess
import psutil

DOWNLOAD_DIR = r"C:\download"
TLAUNCHER_DIR = os.path.join(os.environ['APPDATA'], '.tlauncher', 'legacy', 'Minecraft', 'game')
VERSIONS_DEST = os.path.join(TLAUNCHER_DIR, 'versions')
JAVA_DEST_ROOT = r"C:\Java"
GRAALVM_FOLDER_NAME = "graalvm-jdk-17.0.12+8.1"

def find_exe_folder():
    exes = glob.glob(os.path.join(DOWNLOAD_DIR, "*.exe"))
    if not exes:
        raise FileNotFoundError("Không tìm thấy file .exe TLauncher.")
    return exes[0]

def find_zip(pattern_hint):
    zips = glob.glob(os.path.join(DOWNLOAD_DIR, "*.zip"))
    for z in zips:
        base = os.path.basename(z).lower()
        if pattern_hint.lower() in base:
            return z
    raise FileNotFoundError(f"Không tìm thấy file zip chứa '{pattern_hint}'.")

def wait_for_tlauncher_process():
    print("Đang chờ TLauncher và Java khởi động...")
    while True:
        found = False
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                name = proc.info['name'].lower() if proc.info['name'] else ''
                if 'java' in name:
                    found = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        if found:
            tasklist = subprocess.run('tasklist /fi "IMAGENAME eq javaw.exe" /fo csv /nh',
                                      capture_output=True, text=True, shell=True)
            if 'javaw.exe' in tasklist.stdout:
                print("Đã phát hiện TLauncher/Java đang chạy.")
                input(">>> Nhấn Enter để tiếp tục sau khi bạn đã cài đặt xong TLauncher...")
                return
        time.sleep(3)

def extract_zip(zip_path, extract_to):
    print(f"Giải nén {zip_path} -> {extract_to}")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(extract_to)

def main_workflow():
    print("=== Work.py bắt đầu ===")
    tlauncher_exe = find_exe_folder()
    graalvm_zip = find_zip("graalvm")
    versions_zip = find_zip("versions")
    print("Đã xác nhận đủ 3 file.")

    print("Khởi chạy TLauncher installer. Vui lòng tự cài đặt...")
    subprocess.Popen([tlauncher_exe], shell=True)
    time.sleep(2)

    wait_for_tlauncher_process()

    extract_zip(graalvm_zip, DOWNLOAD_DIR)
    extract_zip(versions_zip, DOWNLOAD_DIR)

    versions_src = os.path.join(DOWNLOAD_DIR, "versions")
    if not os.path.exists(versions_src):
        raise FileNotFoundError("Không tìm thấy thư mục 'versions' sau giải nén.")
    os.makedirs(VERSIONS_DEST, exist_ok=True)
    print(f"Di chuyển versions vào {VERSIONS_DEST}")
    for item in os.listdir(versions_src):
        s = os.path.join(versions_src, item)
        d = os.path.join(VERSIONS_DEST, item)
        if os.path.isdir(s):
            if os.path.exists(d):
                shutil.rmtree(d)
            shutil.move(s, d)
        else:
            shutil.move(s, d)
    try:
        os.rmdir(versions_src)
    except:
        pass

    graalvm_src = os.path.join(DOWNLOAD_DIR, GRAALVM_FOLDER_NAME)
    if not os.path.exists(graalvm_src):
        raise FileNotFoundError(f"Không tìm thấy {graalvm_src}")
    java_dest = os.path.join(JAVA_DEST_ROOT, GRAALVM_FOLDER_NAME)
    os.makedirs(JAVA_DEST_ROOT, exist_ok=True)
    print(f"Di chuyển {graalvm_src} -> {java_dest}")
    if os.path.exists(java_dest):
        shutil.rmtree(java_dest)
    shutil.move(graalvm_src, java_dest)

    print("=== Work.py hoàn tất. Java và versions đã được thiết lập! ===")

if __name__ == '__main__':
    main_workflow()