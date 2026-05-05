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
import json
# Try import, fallback to inlined code for irm | iex
try:
    from mc_utils import find_minecraft_dir
    from config import load_config
except ModuleNotFoundError:
    # Inlined: mc_utils.py
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

    # Inlined: config.py
    def load_config():
        import os
        import yaml
        # Work.py is in Minecraft/, config.yaml is in parent directory
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

cfg = load_config()
DOWNLOAD_DIR = os.path.join(os.environ['USERPROFILE'], 'Downloads')
JAVA_DEST_ROOT = cfg.get('java_dest_root', r'C:\Java')

TLAUNCHER_DIR = find_minecraft_dir()
VERSIONS_DEST = os.path.join(TLAUNCHER_DIR, "versions")
def find_exe_folder():
    tlauncher_candidates = glob.glob(os.path.join(DOWNLOAD_DIR, 'TLauncher*.exe'))
    if tlauncher_candidates:
        tlauncher_candidates.sort(key=os.path.getmtime, reverse=True)
        return tlauncher_candidates[0]
    exes = glob.glob(os.path.join(DOWNLOAD_DIR, '*.exe'))
    if not exes:
        raise FileNotFoundError('Khong tim thay file .exe TLauncher.')
    exes.sort(key=os.path.getmtime, reverse=True)
    return exes[0]


def find_zip(pattern_hint):
    zips = glob.glob(os.path.join(DOWNLOAD_DIR, '*.zip'))
    if not zips:
        raise FileNotFoundError('Khong tim thay file .zip nao trong ' + DOWNLOAD_DIR)
    zips.sort(key=os.path.getmtime, reverse=True)
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
    input('>>> Nhan Enter de tiep tuc sau khi ban da cai dat xong TLauncher...')


def extract_zip(zip_path, extract_to):
    print('Giai nen ' + zip_path + ' -> ' + extract_to)
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(extract_to)


def main_workflow():
    global TLAUNCHER_DIR, VERSIONS_DEST
    TLAUNCHER_DIR = find_minecraft_dir()
    VERSIONS_DEST = os.path.join(TLAUNCHER_DIR, "versions")
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
    graalvm_src = None
    graalvm_folder_name = None
    for item in os.listdir(DOWNLOAD_DIR):
        item_path = os.path.join(DOWNLOAD_DIR, item)
        if os.path.isdir(item_path) and 'graalvm' in item.lower():
            graalvm_src = item_path
            # Xu ly nested: GraalVM.zip/graalvm-jdk-17.0.12+8.1/ -> lay folder con
            subdirs = [
                d for d in os.listdir(graalvm_src)
                if os.path.isdir(os.path.join(graalvm_src, d)) and 'graalvm' in d.lower()
            ]
            if subdirs:
                graalvm_src = os.path.join(graalvm_src, subdirs[0])
                print('[!] Phat hien nested GraalVM, folder con: ' + os.path.basename(graalvm_src))
            graalvm_folder_name = os.path.basename(graalvm_src)
            break

    if not graalvm_src:
        raise FileNotFoundError('Khong tim thay thu muc GraalVM sau giai nen trong ' + DOWNLOAD_DIR)
    print('[+] Tim thay GraalVM tai: ' + graalvm_src)

    versions_src = os.path.join(DOWNLOAD_DIR, 'versions')
    if not os.path.exists(versions_src):
        raise FileNotFoundError("Khong tim thay thu muc 'versions' sau giai nen.")
    os.makedirs(VERSIONS_DEST, exist_ok=True)
    print('Di chuyen versions vao ' + VERSIONS_DEST)
    for item in os.listdir(versions_src):
        s = os.path.join(versions_src, item)
        d = os.path.join(VERSIONS_DEST, item)
        try:
            if os.path.isdir(s):
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.move(s, d)
            else:
                shutil.move(s, d)
        except Exception as e:
            raise RuntimeError('Loi khi di chuyen ' + s + ' -> ' + d + ': ' + str(e))
    try:
        os.rmdir(versions_src)
    except Exception as e:
        print('[!] Khong the xoa thu muc ' + versions_src + ': ' + str(e))

    # Di chuyen GraalVM vao thu muc Java (dung ten thu muc con)
    java_dest = os.path.join(JAVA_DEST_ROOT, graalvm_folder_name if graalvm_folder_name else os.path.basename(graalvm_src))
    os.makedirs(JAVA_DEST_ROOT, exist_ok=True)
    print('Di chuyen ' + graalvm_src + ' -> ' + java_dest)
    try:
        if os.path.exists(java_dest):
            shutil.rmtree(java_dest)
        shutil.move(graalvm_src, java_dest)
    except Exception as e:
        raise RuntimeError('Loi khi di chuyen GraalVM: ' + str(e))

    # Tao config TLauncher tu dong nhan GraalVM
    java_exe = os.path.join(java_dest, 'bin', 'java.exe')
    config = {"javaPaths": [java_exe]}
    # Luu tai AppData\Roaming\.tlauncher (vi tri chuan)
    tlauncher_config_dir = os.path.join(os.environ['APPDATA'], '.tlauncher')
    os.makedirs(tlauncher_config_dir, exist_ok=True)
    config_path = os.path.join(tlauncher_config_dir, 'minecraft_tlauncher_java_config.json')
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    print('[+] Da tao config TLauncher: ' + config_path)

    print('=== Work.py hoan tat. Java va versions da duoc thiet lap! ===')


if __name__ == '__main__':
    main_workflow()


