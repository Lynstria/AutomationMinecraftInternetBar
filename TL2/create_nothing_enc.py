#!/usr/bin/env python3
"""Create nothing.enc from API files."""
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib_pure'))
from aes_pure import aes256_encrypt
from hashlib import sha256

def main():
    if len(sys.argv) < 5:
        print("Usage: python create_nothing_enc.py <password> <discord_file> <refresh_file> <client_json>")
        print("  password: mã bảo mật để mã hóa")
        print("  discord_file: đường dẫn tới file DIS.txt")
        print("  refresh_file: đường dẫn tới file RefreshToken.txt")
        print("  client_json: đường dẫn tới file client_secret_*.json")
        sys.exit(1)
    password = sys.argv[1]
    discord_file = sys.argv[2]
    refresh_file = sys.argv[3]
    client_json = sys.argv[4]
    # Read Discord webhook
    with open(discord_file, 'r') as f:
        discord_url = f.read().strip()
    # Read refresh token
    with open(refresh_file, 'r') as f:
        refresh_token = f.read().strip()
    # Read client_id from JSON
    with open(client_json, 'r') as f:
        client_data = json.load(f)
    client_id = client_data['web']['client_id']
    client_secret = client_data['web']['client_secret']
    # Construct payload
    payload = json.dumps({"discord": discord_url, "refresh_token": refresh_token, "client_id": client_id, "client_secret": client_secret}, ensure_ascii=False)
    print(f"Payload length: {len(payload)} bytes")
    key = sha256(password.encode()).digest()
    # Encrypt
    ciphertext = aes256_encrypt(key, payload.encode('utf-8'))
    # Write nothing.enc
    out_path = os.path.join(os.path.dirname(__file__), 'nothing.enc')
    with open(out_path, 'wb') as f:
        f.write(ciphertext)
    print(f"Created {out_path} ({len(ciphertext)} bytes)")

if __name__ == '__main__':
    main()
