# Issue #5: Deepen crypto module ✅ COMPLETED

## Parent
N/A - From /improve-codebase-architecture session

## What to build
Tách `decrypt_secrets.py` thành 2 modules: `crypto_utils.py` (pure decryption logic, trả về dict) và `decrypt_secrets.py` (thin CLI wrapper).

## Acceptance criteria
- [x] Tạo `crypto_utils.py` với hàm `decrypt_secrets_file(path, password)` trả về dict {discord_webhook, google_credentials_json}
- [x] `decrypt_secrets.py` chỉ là CLI wrapper gọi `crypto_utils`
- [x] Output là JSON thuần túy (không lẫn text khác)
- [x] Main.ps1 parse JSON thay vì parse stdout dòng-by-dòng
- [x] Test: TDD cycle (RED-GREEN-REFACTOR) ✅
- [x] Tất cả tests pass ✅

## Blocked by
None - completed

## Labels
refactor, ready-for-agent, completed
