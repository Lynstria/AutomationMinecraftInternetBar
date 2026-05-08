r"""Exec.py - Install Tlauncher, extract GraalVM, setup Java.
# -*- coding: utf-8 -*-
Stdlib only: subprocess, zipfile, os, shutil.
"""

import os
import sys
import subprocess
import shutil


def setup_logging():
    r"""Setup logging. Read log path from %TEMP%\mc_log_path.txt."""
    import logging
    log_path_file = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "mc_log_path.txt")
    if os.path.exists(log_path_file):
        with open(log_path_file, encoding="utf-8-sig") as f:
            log_file = f.read().strip()
    else:
        log_file = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "exec.log")

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    return logging.getLogger(__name__)


def read_download_path():
    r"""Read download dir from %TEMP%\mc_path.txt. Return path or None."""
    temp_dir = os.environ.get("TEMP", "C:\\Temp")
    mc_path_file = os.path.join(temp_dir, "mc_path.txt")
    if not os.path.exists(mc_path_file):
        return None
    with open(mc_path_file, encoding="utf-8-sig") as f:
        path = f.read().strip()
    return path if path else None


def find_folder_case_insensitive(parent, pattern):
    """Find folder in parent dir containing pattern (case-insensitive). Return full path or None."""
    if not os.path.isdir(parent):
        return None
    for entry in os.listdir(parent):
        full = os.path.join(parent, entry)
        if os.path.isdir(full) and pattern.lower() in entry.lower():
            return full
    return None


def extract_zip(zip_path, dest_dir):
    """Extract zip to dest dir. Return True on success."""
    import zipfile
    try:
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(dest_dir)
        return True
    except Exception:
        return False


def run_tlauncher_installer(installer_path):
    """Run Tlauncher installer. Wait for process exit. Return True on success."""
    try:
        subprocess.run([installer_path], check=True)
        return True
    except Exception:
        return False


def setup_java(graalvm_zip_path, downloads_dir):
    r"""Extract GraalVM, move to C:\Java\. Return java.exe path or None."""
    # Extract GraalVM
    extract_dir = os.path.join(downloads_dir, "graalvm_extract")
    if not extract_zip(graalvm_zip_path, extract_dir):
        return None

    # Find graalvm folder
    graalvm_dir = find_folder_case_insensitive(extract_dir, "graalvm")
    if not graalvm_dir:
        return None

    # Create C:\Java\ if not exists
    java_dir = "C:\\Java"
    if not os.path.exists(java_dir):
        os.makedirs(java_dir)

    # Move graalvm to C:\Java\
    dest = os.path.join(java_dir, os.path.basename(graalvm_dir))
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.move(graalvm_dir, java_dir)

    # Find java.exe
    java_exe = os.path.join(java_dir, os.path.basename(graalvm_dir), "bin", "java.exe")
    return java_exe if os.path.exists(java_exe) else None


def install_versions(versions_zip_path, downloads_dir):
    r"""Extract versions.zip, move versions folder to .minecraft\. Return True on success."""
    # Find .minecraft folder
    minecraft_dir = None
    for appdata in ["APPDATA", "LOCALAPPDATA"]:
        base = os.environ.get(appdata)
        if not base:
            continue
        for root, dirs, _ in os.walk(base):
            for d in dirs:
                if "minecraft" in d.lower():
                    minecraft_dir = os.path.join(root, d)
                    break
            if minecraft_dir:
                break
        if minecraft_dir:
            break

    if not minecraft_dir:
        return False

    # Extract versions.zip
    extract_dir = os.path.join(downloads_dir, "versions_extract")
    if not extract_zip(versions_zip_path, extract_dir):
        return False

    # Find versions folder
    versions_dir = find_folder_case_insensitive(extract_dir, "versions")
    if not versions_dir:
        return False

    # Move to .minecraft\
    dest = os.path.join(minecraft_dir, "versions")
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.move(versions_dir, minecraft_dir)

    return True


def run_exec():
    """Main entry point. Read path, run installer, setup Java, install versions."""
    downloads_dir = read_download_path()
    if not downloads_dir:
        return False

    logger = setup_logging()
    logger.info("Starting Exec.py, downloads_dir=%s", downloads_dir)

    # Find installer
    tlauncher_exe = os.path.join(downloads_dir, "Tlauncher-Installer-1.9.5.1.exe")
    if os.path.exists(tlauncher_exe):
        logger.info("Running Tlauncher installer...")
        run_tlauncher_installer(tlauncher_exe)

    # Setup Java
    graalvm_zip = os.path.join(downloads_dir, "GraalVM.zip")
    if os.path.exists(graalvm_zip):
        logger.info("Setting up Java from GraalVM...")
        java_exe = setup_java(graalvm_zip, downloads_dir)
        if java_exe:
            logger.info("Java setup OK: %s", java_exe)

    # Install versions
    versions_zip = os.path.join(downloads_dir, "versions.zip")
    if os.path.exists(versions_zip):
        logger.info("Installing versions...")
        install_versions(versions_zip, downloads_dir)

    logger.info("Exec.py completed")
    return True


if __name__ == "__main__":
    run_exec()
