#!/usr/bin/env python3
"""
mc_utils.py - Shared utilities for Minecraft automation.
Contains common functions extracted from Work.py and Upload.py.
"""

import os
import sys


def find_minecraft_dir():
    """Tự động tìm thư mục Minecraft, hoạt động trên mọi máy (cả quán net)."""
    appdata_locations = set()

    # Các biến môi trường chuẩn
    for var in ["APPDATA", "LOCALAPPDATA"]:
        if var in os.environ:
            appdata_locations.add(os.environ[var])

    # LocalLow (cùng parent với Local)
    if "LOCALAPPDATA" in os.environ:
        appdata_locations.add(os.path.join(os.path.dirname(os.environ["LOCALAPPDATA"]), "LocalLow"))

    # Tự động tìm qua USERPROFILE (máy quán net)
    if "USERPROFILE" in os.environ:
        appdata_locations.add(os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming"))
        appdata_locations.add(os.path.join(os.environ["USERPROFILE"], "AppData", "Local"))
        appdata_locations.add(os.path.join(os.environ["USERPROFILE"], "AppData", "LocalLow"))

    # Nếu không có gì hết, thử với đường dẫn mặc định
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
        # Tìm .tlauncher (không phân biệt in hoa/thường)
        for d in os.listdir(base):
            full = os.path.join(base, d)
            if d.lower() == ".tlauncher" and os.path.isdir(full):
                # Tìm legacy/Minecraft/game
                for root, dirs, files in os.walk(full):
                    for subd in dirs:
                        if subd.lower() == "game":
                            game_dir = os.path.join(root, subd)
                            if os.path.exists(game_dir):
                                candidates.append(game_dir)
                # Tìm Minecraft/game (không có legacy)
                mc_game = os.path.join(full, "Minecraft", "game")
                if os.path.exists(mc_game):
                    candidates.append(mc_game)

        # Tìm .minecraft (không phân biệt in hoa/thường)
        for d in os.listdir(base):
            full = os.path.join(base, d)
            if d.lower() == ".minecraft" and os.path.isdir(full):
                candidates.append(full)
                break

    if not candidates:
        tried = "\n".join(str(p) for p in appdata_locations)
        raise FileNotFoundError(
            "Không tìm thấy thư mục Minecraft trong AppData.\n"
            f"Đã thử các vị trí:\n{tried}"
        )

    return candidates[0]
