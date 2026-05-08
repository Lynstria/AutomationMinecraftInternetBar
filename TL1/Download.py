"""Download.py - Download 3 files: Tlauncher.exe, GraalVM.zip, versions.zip.
# -*- coding: utf-8 -*-
Stdlib only: urllib.request, zipfile, json, os, shutil.
"""

import os
import sys
import urllib.request
import time
import re


TLUANCHER_FALLBACK = "https://dl1.tlauncher.org/f.php?f=files%2FTLauncher-Installer-1.9.5.1.exe"
GRAALVM_ID = "1xrxfMiLBWOS2ptPOnUClHrNXOuozid_a"
VERSIONS_ID = "1_JH04cXYbWSbhTmn3Y9jQFAf57DayWNM"
GDRIVE_URL = "https://drive.google.com/uc?export=download&id={}"


def get_downloads_folder():
    """Find user Downloads folder. Scan C: for Downloads if standard path fails."""
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        standard = os.path.join(user_profile, "Downloads")
        if os.path.isdir(standard):
            return standard

    for root, dirs, _ in os.walk("C:\\", topdown=True):
        for d in dirs:
            if d.lower() == "downloads":
                return os.path.join(root, d)
        if root.count(os.sep) > 5:
            dirs.clear()

    return os.environ.get("TEMP", "C:\\Temp")


def _parse_gdrive_form(html):
    """Extract form action + hidden fields from virus warning page."""
    form_match = re.search(r'<form[^>]*action="([^"]+)"[^>]*>(.*?)</form>', html, re.DOTALL)
    if not form_match:
        return None, {}

    action = form_match.group(1)
    form_body = form_match.group(2)

    fields = {}
    for match in re.finditer(r'<input[^>]*name="([^"]+)"[^>]*value="([^"]*)"', form_body):
        fields[match.group(1)] = match.group(2)

    return action, fields


def _download_gdrive(url, dest, timeout=300):
    """Download from Google Drive with streaming. Handle virus warning confirm."""
    import tempfile
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        body = resp.read()
    except urllib.error.HTTPError as e:
        body = e.read()

    html = body.decode("utf-8", errors="ignore")

    # Check for virus warning page
    if "Virus scan warning" in html or "download_warning" in html:
        action, fields = _parse_gdrive_form(html)
        if action and fields:
            params = "&".join(f"{k}={v}" for k, v in fields.items())
            url = action + "?" + params
            req = urllib.request.Request(url, headers=headers)
            try:
                resp = urllib.request.urlopen(req, timeout=timeout)
            except urllib.error.HTTPError as e:
                resp = e

            # Stream to temp file
            tmp = dest + ".part"
            with open(tmp, "wb") as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
            os.replace(tmp, dest)
            return os.path.exists(dest) and os.path.getsize(dest) > 1000

    # Direct download (small file)
    tmp = dest + ".part"
    with open(tmp, "wb") as f:
        f.write(body)
    os.replace(tmp, dest)
    return os.path.exists(dest) and os.path.getsize(dest) > 1000


def download_file(url, dest, retries=3, timeout=300):
    """Download URL to dest with streaming. Retry on fail. Return True on success."""
    for attempt in range(retries):
        try:
            if "drive.google.com" in url:
                return _download_gdrive(url, dest, timeout)

            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                tmp = dest + ".part"
                with open(tmp, "wb") as f:
                    while True:
                        chunk = resp.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                os.replace(tmp, dest)
            return os.path.exists(dest) and os.path.getsize(dest) > 0
        except Exception:
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
    return False


def download_tlauncher(dest_dir):
    """Download Tlauncher installer. Return path on success, None on fail."""
    dest = os.path.join(dest_dir, "Tlauncher-Installer-1.9.5.1.exe")
    ok = download_file(TLUANCHER_FALLBACK, dest)
    return dest if ok else None


def download_graalvm(dest_dir):
    """Download GraalVM.zip from Google Drive. Return path or None."""
    dest = os.path.join(dest_dir, "GraalVM.zip")
    url = GDRIVE_URL.format(GRAALVM_ID)
    ok = download_file(url, dest)
    return dest if ok else None


def download_versions(dest_dir):
    """Download versions.zip from Google Drive. Return path or None."""
    dest = os.path.join(dest_dir, "versions.zip")
    url = GDRIVE_URL.format(VERSIONS_ID)
    ok = download_file(url, dest)
    return dest if ok else None


def setup_logging():
    """Setup logging. Read log path from %TEMP%\mc_log_path.txt."""
    import logging
    log_path_file = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "mc_log_path.txt")
    if os.path.exists(log_path_file):
        with open(log_path_file, encoding="utf-8-sig") as f:
            log_file = f.read().strip()
    else:
        log_file = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "download.log")

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    return logging.getLogger(__name__)


def run_downloads(dest_dir=None):
    """Download all 3 files. Return dict with paths. Write mc_path.txt."""
    if dest_dir is None:
        dest_dir = get_downloads_folder()

    logger = setup_logging()
    logger.info("Starting downloads to %s", dest_dir)

    results = {}
    files = [
        ("tlauncher", "Tlauncher-Installer-1.9.5.1.exe", download_tlauncher),
        ("graalvm", "GraalVM.zip", download_graalvm),
        ("versions", "versions.zip", download_versions),
    ]

    idx = 0
    for name, display_name, func in files:
        idx += 1
        print(f"[{idx}/3] Downloading {display_name}...")
        logger.info("Downloading %s...", name)
        path = func(dest_dir)
        if path:
            size = os.path.getsize(path)
            print(f"  {display_name} OK ({size} bytes)")
            logger.info("%s OK: %s (%d bytes)", name, path, size)
            results[name] = path
        else:
            print(f"  {display_name} FAILED!")
            logger.error("%s FAILED", name)

    # Write download dir path to mc_path.txt
    mc_path_file = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "mc_path.txt")
    with open(mc_path_file, "w") as f:
        f.write(dest_dir)

    logger.info("Download dir written to %s", mc_path_file)
    return results


if __name__ == "__main__":
    run_downloads()
