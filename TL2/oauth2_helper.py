#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OAuth2 helper - use refresh_token to get access_token for Drive API."""
import sys, os, json, urllib.request, urllib.parse

def get_access_token(refresh_token, client_id, client_secret):
    """Exchange refresh_token for access_token."""
    data = urllib.parse.urlencode({
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }).encode('utf-8')
    req = urllib.request.Request(
        'https://oauth2.googleapis.com/token',
        data=data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    resp = urllib.request.urlopen(req, timeout=10)
    result = json.loads(resp.read().decode('utf-8'))
    return result['access_token']

def main():
    if len(sys.argv) < 4:
        print("Usage: python oauth2_helper.py <refresh_token> <client_id> <client_secret>")
        sys.exit(1)
    token = get_access_token(sys.argv[1], sys.argv[2], sys.argv[3])
    print(token)

if __name__ == '__main__':
    main()
