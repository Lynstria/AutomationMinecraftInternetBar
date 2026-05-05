# Issue #1: Fix OTP generation + interactive Python execution

## Parent
N/A - Root issue from /diagnose session

## What to build
Sửa Defends.py để sinh OTP từ digit pool (0-9) thay vì đọc env var sai. Sửa Main.ps1 để bỏ `2>&1` khi chạy Python interactive, cho phép nhập OTP trực tiếp từ console mà không bị PowerShell bắt output.

## Acceptance criteria
- [ ] Defends.py không còn đọc `os.environ.get("246810")` - thay bằng `DIGIT_POOL = "0123456789"`
- [ ] `generate_otp()` chọn 4 số ngẫu nhiên từ pool, xáo trộn bằng `secrets.SystemRandom()`
- [ ] Main.ps1 dòng 144: bỏ `2>&1` khi `$Interactive = $true`
- [ ] Test: Chạy Defends.py trực tiếp, nhập OTP từ Discord, xác thực thành công
- [ ] Không còn lỗi "Thiếu OTP_SECRET"

## Blocked by
None - can start immediately

## Labels
bug, feature, ready-for-agent
