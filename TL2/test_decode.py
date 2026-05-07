import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from hashlib import sha256

def test_decrypt_correct_password():
    """Decrypt nothing.enc with correct password -> get dict."""
    from Decode import decrypt_nothing_enc
    result = decrypt_nothing_enc("Lynstria")
    assert result is not None, "Should decrypt"
    assert "discord" in result, "Missing discord field"
    assert "drive" in result, "Missing drive field"
    print("PASS: decrypt correct password")

def test_decrypt_wrong_password():
    from Decode import decrypt_nothing_enc
    result = decrypt_nothing_enc("wrong")
    assert result is None, "Should return None for wrong password"
    print("PASS: decrypt wrong password")

def test_discord_api_valid():
    from Decode import test_discord_api
    # Use a known invalid URL (should return False)
    assert test_discord_api("https://invalid.url") == False
    print("PASS: discord API invalid")

if __name__ == '__main__':
    test_decrypt_correct_password()
    test_decrypt_wrong_password()
    test_discord_api_valid()
    print("ALL PASS")
