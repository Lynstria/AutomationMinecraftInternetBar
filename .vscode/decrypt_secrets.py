#!/usr/bin/env python3
"""
decrypt_secrets.py - Thin CLI wrapper for decryption.
Uses crypto_utils for actual decryption logic. Outputs JSON.
"""

import os
import sys
import getpass
import tempfile
import json
import atexit

# Add parent directory to path so crypto_utils can be found
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto_utils import decrypt_secrets_file

# Global variables for tracking temp file
_temp_file_path = None
_success = False

MAX_ATTEMPTS = 3


def cleanup_temp_file():
    """Cleanup temp file if script exits unsuccessfully."""
    global _temp_file_path
    if _temp_file_path and os.path.exists(_temp_file_path) and not _success:
        try:
            os.unlink(_temp_file_path)
            print(f"[!] Da xoa file tam: {_temp_file_path}", file=sys.stderr)
        except:
            pass


def main():
    global _temp_file_path, _success

    # Get secrets.enc path from command line or default
    if len(sys.argv) > 1:
        secrets_path = sys.argv[1]
    else:
        secrets_path = "secrets.enc"

    if not os.path.exists(secrets_path):
        print(f"[ERROR] Khong tim thay file {secrets_path}.", file=sys.stderr)
        sys.exit(1)

    for attempt in range(1, MAX_ATTEMPTS + 1):
        if len(sys.argv) > 2:
            password = sys.argv[2]  # Password passed as argument
        else:
            password = getpass.getpass("🔑 Nhap ma API: ")
        try:
            result = decrypt_secrets_file(secrets_path, password)

            # Write credentials to temp file
            tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
            tmp.write(result['google_credentials_json'])
            tmp.close()
            _temp_file_path = tmp.name

            # Register cleanup
            atexit.register(cleanup_temp_file)

            # Output JSON for PowerShell to parse
            output = {
                "discord_webhook": result['discord_webhook'],
                "google_credentials_path": tmp.name
            }
            print(json.dumps(output))
            _success = True
            sys.exit(0)
        except Exception:
            print("❌ Sai ma API. Vui long thu lai.", file=sys.stderr)
            if attempt == MAX_ATTEMPTS:
                print("Ban da nhap sai qua so lan cho phep.", file=sys.stderr)
                sys.exit(1)

if __name__ == "__main__":
    main()
