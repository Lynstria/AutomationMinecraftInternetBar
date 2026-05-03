#!/usr/bin/env python3
"""
Work.py (Repo: Lynstria/AutomationMinecraftInternetBar)
- Quet thu muc Downloads, chay TLauncher installer.
- Theo doi tien trinh Java + TLauncher.
- Giai nen, di chuyen version va Java.
"""

import os
import sys
import glob
import time
import shutil
import zipfile
import subprocess
import psutil

DOWNLOAD_DIR = os.path.join(os.environ['USERPROFILE'], 'Downloads')
TLAUNCHER_DIR = os.path.join(os.environ['APPDATA'], '.tlauncher', 'legacy', 'Minecraft', 'game')
VERSIONS_DEST = os.path.join(TLAUNCHER_DIR, 'versions')
JAVA_DEST_ROOT = r'C:\Java'


def find_exe_folder():
    tlauncher_candidates = glob.glob(os.path.join(DOWNLOAD_DIR, 'TLauncher*.exe'))
    if tlauncher_candidates:
        return tlauncher_candidates[0]
    exes = glob.glob(os.path.join(DOWNLOAD_DIR, '*.exe'))
    if not exes:
        raise FileNotFoundError('Khong tim thay file .exe TLauncher.')
    return exes[0]


def find_zip(pattern_hint):
    zips = glob.glob(os.path.join(DOWNLOAD_DIR, '*.zip'))
    if not zips:
        raise FileNotFoundError('Khong tim thay file .zip nao trong ' + DOWNLOAD_DIR)
    for z in zips:
        base = os.path.basename(z).lower()
        if pattern_hint.lower() in base:
            return z
    if len(zips) == 1:
        print('[!] Khong tim thay pattern ' + pattern_hint + ', dung file duy nhat: ' + os.path.basename(zips[0]))
        return zips[0]
    zip_names = [os.path.basename(z) for z in zips]
    raise FileNotFoundError(
        'Khong tim thay file zip chua ' + pattern_hint + '.\n'
        'Cac file zip hien co: ' + ', '.join(zip_names)
    )


def wait_for_tlauncher_process():
    print('Dang cho TLauncher va Java khoi dong...')
    while True:
        found = False
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                name = (proc.info['name'] or '').lower()
                if 'java' in name:
                    found = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        if found:
            print('Da phat hien TLauncher/Java dang chay.')
            input('>>> Nhan Enter de tiep tuc sau khi ban da cai dat xong TLauncher...')
            return
        time.sleep(3)


def extract_zip(zip_path, extract_to):
    print('Giai nen ' + zip_path + ' -> ' + extract_to)
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(extract_to)


def main_workflow():
    print('=== Work.py bat dau ===')
    tlauncher_exe = find_exe_folder()
    graalvm_zip = find_zip('graalvm')
    versions_zip = find_zip('versions')
    print('Da xac nhan du 3 file.')

    print('Khoi chay TLauncher installer. Vui long tu cai dat...')
    subprocess.Popen(tlauncher_exe)
    time.sleep(2)

    wait_for_tlauncher_process()

    extract_zip(graalvm_zip, DOWNLOAD_DIR)
    extract_zip(versions_zip, DOWNLOAD_DIR)

    # Tim thu muc GraalVM dong
    graalvm_dirs = [
        d for d in os.listdir(DOWNLOAD_DIR)
        if os.path.isdir(os.path.join(DOWNLOAD_DIR, d)) and 'graalvm' in d.lower()
    ]
    if not graalvm_dirs:
        raise FileNotFoundError('Khong tim thay thu muc GraalVM sau giai nen trong ' + DOWNLOAD_DIR)
    graalvm_src = os.path.join(DOWNLOAD_DIR, graalvm_dirs[0])
    if len(graalvm_dirs) > 1:
        print('[!] Co nhieu thu muc GraalVM, dung: ' + graalvm_dirs[0])

    versions_src = os.path.join(DOWNLOAD_DIR, 'versions')
    if not os.path.exists(versions_src):
        raise FileNotFoundError("Khong tim thay thu muc 'versions' sau giai nen.")
    os.makedirs(VERSIONS_DEST, exist_ok=True)
    print('Di chuyen versions vao ' + VERSIONS_DEST)
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
    except Exception:
        pass

    # Di chuyen GraalVM vao thu muc Java
    java_dest = os.path.join(JAVA_DEST_ROOT, graalvm_dirs[0])
    os.makedirs(JAVA_DEST_ROOT, exist_ok=True)
    print('Di chuyen ' + graalvm_src + ' -> ' + java_dest)
    if os.path.exists(java_dest):
        shutil.rmtree(java_dest)
    shutil.move(graalvm_src, java_dest)

    print('=== Work.py hoan tat. Java va versions da duoc thiet lap! ===')


if __name__ == '__main__':
    main_workflow()
