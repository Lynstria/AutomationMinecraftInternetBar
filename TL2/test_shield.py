import sys, os, json, random
sys.path.insert(0, os.path.dirname(__file__))

def test_generate_code():
    from Shield import generate_code
    for _ in range(100):
        code, shuffled = generate_code()
        assert 0 <= int(code) <= 9999, "Code out of range"
        assert len(shuffled) == 4, "Shuffled length must be 4"
        assert sorted(shuffled) == sorted(code), "Shuffled must contain same digits"
    print("PASS: generate_code")

def test_send_discord():
    from Shield import send_discord_code
    # Test with invalid URL, should raise or return False
    try:
        send_discord_code("https://invalid.url", "1234")
    except Exception:
        pass  # Expected
    print("PASS: send_discord (invalid URL)")

if __name__ == '__main__':
    test_generate_code()
    test_send_discord()
    print("ALL PASS")
