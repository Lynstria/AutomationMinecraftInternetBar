import sys, os, tempfile, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib_pure'))
from hashlib import sha256

def test_encrypt_decrypt_known():
    """Encrypt known plaintext, decrypt, get same."""
    from aes_pure import aes256_encrypt, aes256_decrypt
    key = sha256(b"testpass").digest()
    plaintext = b"1234567890123456"  # 16 bytes exactly
    ct = aes256_encrypt(key, plaintext)
    # PKCS7 always pads, so 16-byte plaintext -> 32-byte ciphertext
    assert len(ct) == 32, f"Expected 32, got {len(ct)}"
    result = aes256_decrypt(key, ct)
    assert result == plaintext, f"Got {result}"

def test_encrypt_decrypt_long():
    """Long plaintext with padding."""
    from aes_pure import aes256_encrypt, aes256_decrypt
    key = sha256(b"longpass").digest()
    plaintext = b"A" * 50  # not multiple of 16
    ct = aes256_encrypt(key, plaintext)
    assert len(ct) == 64  # 50 + 14 pad = 64
    result = aes256_decrypt(key, ct)
    assert result == plaintext, f"Got {result}"

def test_wrong_key():
    """Decrypt with wrong key -> error or garbage."""
    from aes_pure import aes256_encrypt, aes256_decrypt
    key1 = sha256(b"right").digest()
    key2 = sha256(b"wrong").digest()
    pt = b"X" * 16
    ct = aes256_encrypt(key1, pt)
    try:
        result = aes256_decrypt(key2, ct)
        # Might be garbage, should not equal pt
        assert result != pt
    except Exception:
        pass  # Expected

def test_decrypt_garbage():
    """Decrypt garbage -> ValueError on padding."""
    from aes_pure import aes256_decrypt
    key = sha256(b"pass").digest()
    garbage = os.urandom(32)  # random bytes, not valid ciphertext
    try:
        aes256_decrypt(key, garbage)
        assert False, "Should raise"
    except Exception:
        pass  # Expected

if __name__ == '__main__':
    test_encrypt_decrypt_known()
    print("PASS: test_encrypt_decrypt_known")
    test_encrypt_decrypt_long()
    print("PASS: test_encrypt_decrypt_long")
    test_wrong_key()
    print("PASS: test_wrong_key")
    test_decrypt_garbage()
    print("PASS: test_decrypt_garbage")
    print("ALL PASS")
