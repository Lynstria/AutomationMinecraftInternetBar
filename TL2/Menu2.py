#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Menu2.py - TL2 menu: 1=Upload, 2=Manager"""
import sys, os, subprocess

TL2_DIR = os.path.dirname(os.path.abspath(__file__))
STAGE_UPLOAD = os.path.join(TL2_DIR, 'Stage_upload')

def main():
    while True:
        print("\n=== TL2 Menu ===")
        print("1. Upload versions to Drive")
        print("2. Manager - Quản lý versions")
        print("3. Thoát về Menu chính")
        try:
            choice = input("Chọn (1-3): ").strip()
        except EOFError:
            print("No input")
            sys.exit(1)

        if choice == '1':
            upload_py = os.path.join(STAGE_UPLOAD, 'Upload.py')
            if not os.path.exists(upload_py):
                print(f"Không tìm thấy {upload_py}")
                continue
            ret = subprocess.call([sys.executable, upload_py])
            if ret != 0:
                print("Upload thất bại")
        elif choice == '2':
            manager_py = os.path.join(STAGE_UPLOAD, 'Manager.py')
            if not os.path.exists(manager_py):
                print(f"Không tìm thấy {manager_py}")
                continue
            ret = subprocess.call([sys.executable, manager_py])
            if ret != 0:
                print("Manager thất bại")
        elif choice == '3':
            print("Thoát về menu chính...")
            return
        else:
            print("Chọn 1-3")

if __name__ == '__main__':
    main()
