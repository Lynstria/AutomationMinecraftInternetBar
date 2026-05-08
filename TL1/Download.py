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


def _is_html(data):
    """Check if data starts with HTML tags."""
    if not data:
        return False
    head = data[:512].strip().lower()
    return head.startswith(b"<!doctype") or head.startswith(b"<html") or b"<html" in head


def _download_gdrive(url, dest, timeout=300):
    """Download from Google Drive with streaming. Handle virus warning confirm."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    # First request
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        first_chunk = resp.read(8192)
    except urllib.error.HTTPError as e:
        first_chunk = e.read(8192) if hasattr(e, 'read') else b""
        resp = e
    except Exception:
        return False

    if not first_chunk:
        return False

    # Check if response is virus warning page
    if _is_html(first_chunk):
        html_bytes = first_chunk
        if hasattr(resp, 'read'):
            try:
                html_bytes += resp.read()
            except:
                pass
        html = html_bytes.decode("utf-8", errors="ignore")

        # Parse form from virus warning page
        action, fields = _parse_gdrive_form(html)
        if not action or "confirm" not in fields:
            return False

        # Build URL from form action + all fields
        params = "&".join(f"{k}={v}" for k, v in fields.items())
        url2 = action + "?" + params
        req2 = urllib.request.Request(url2, headers=headers)
        try:
            resp2 = urllib.request.urlopen(req2, timeout=timeout)
            # Check if still HTML (some cases need additional auth)
            chunk2 = resp2.read(8192)
            if _is_html(chunk2):
                return False
            # Stream remaining data
            class FakeResp2:
                def __init__(self, first, resp):
                    self.first = first
                    self.resp = resp
                    self._used = False
                def read(self, n=-1):
                    if not self._used:
                        self._used = True
                        return self.first
                    if self.resp:
                        try:
                            return self.resp.read(n)
                        except:
                            pass
                    return b""
            fake2 = FakeResp2(chunk2, resp2)
            return _stream_to_file(fake2, dest, timeout)
        except Exception:
            return False

    # Not virus warning - stream the file
    class FakeResp:
        def __init__(self, first, resp):
            self.first = first
            self.resp = resp
            self._used = False
        def read(self, n=-1):
            if not self._used:
                self._used = True
                return self.first
            if self.resp:
                try:
                    return self.resp.read(n)
                except:
                    pass
            return b""

    fake = FakeResp(first_chunk, resp if 'resp' in locals() else None)
    return _stream_to_file(fake, dest, timeout)


def _stream_to_file(resp, dest, timeout=300):
    """Stream response to temp file, then atomically replace."""
    tmp = dest + ".part"
    try:
        with open(tmp, "wb") as f:
            while True:
                try:
                    chunk = resp.read(8192)
                except:
                    break
                if not chunk:
                    break
                f.write(chunk)
        if os.path.exists(tmp) and os.path.getsize(tmp) > 0:
            os.replace(tmp, dest)
            return True
        return False
    except Exception:
        return False
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except:
                pass


def download_file(url, dest, retries=3, timeout=300):
    """Download URL to dest with streaming. Retry on fail. Return True on success."""
    for attempt in range(retries):
        try:
            if "drive.google.com" in url:
                return _download_gdrive(url, dest, timeout)

            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return _stream_to_file(resp, dest, timeout)
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
    """Setup logging. Read log path from %TEMP%\\mc_log_path.txt."""
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
    total = len(files)
    for name, display_name, func in files:
        idx += 1
        print(f"[{idx}/{total}] Downloading {display_name}...")
        logger.info("Downloading %s...", name)
        path = func(dest_dir)
        if path:
            logger.info("%s OK: %s", name, path)
            results[name] = path
        else:
            print(f"  {display_name} FAILED!")
            logger.error("%s FAILED", name)

        # Delay 2s between files for network stability
        if idx < total:
            time.sleep(2)

    # Write download dir path to mc_path.txt
    mc_path_file = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "mc_path.txt")
    with open(mc_path_file, "w", encoding="utf-8") as f:
        f.write(dest_dir)

    logger.info("Download dir written to %s", mc_path_file)
    return results


if __name__ == "__main__":
    run_downloads()
