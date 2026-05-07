# Bài học kinh nghiệm - AutomationMinecraftInternetBar

## Phiên bản ổn định
- **v1.0-stable** (ec506f3 "Up README") — Tag: `v1.0-stable`
- TL1: Download + Install + Java setup (ổn định)
- TL2: Upload maps (REMOVED sau rollback 2026-05-08)

## Kiến trúc
- 2 lớp bảo mật: BreakAES (decrypt) + Shield (4 digits Discord)
- Env vars cho secrets: `$env:DISCORD_WEBHOOK`, `$env:DRIVE_TOKEN_JSON`
- Password prompt: 4 attempts, decrypt `nothing.enc`

## TDD Lessons
- Red-Green-Refactor loop hiệu quả
- Viết test trước, sau đó implement tối thiểu
- Verify tất cả tests pass trước khi commit
- BreakAES: 6/6 tests pass (trước rollback)
- TL2: 31/31 tests pass (trước rollback)

## Bugs đã fix (trước rollback)
- `$PSScriptRoot` rỗng khi chạy `irm | iex` (Main.ps1 dòng 26)
- `ModuleNotFoundError` (crypto_utils, mc_utils, config)
- BreakAES: join separator, kp01-16 numbering, self-scan, duplicate prefix, extra unpad

## Quyết định Rollback (2026-05-08)
- TL2 quá phức tạp (Google Drive API, xóa rclone)
- User quyết định v1.0 (Up README) ổn định nhất
- Hard reset về ec506f3 + force push + tag v1.0-stable
- Mất: TL2 work (Shield, Upload, VersionMenu, test files)

## Skills đã dùng
- `/remember` — Đọc context từ docs/
- `/caveman` — Ultra-compressed communication
- `/tdd` — Test-driven development
- `/diagnose` — Debug bugs
- `/brainstorming` — Lên kế hoạch TL2
- `/grill-me` — Stress-test plan
- `/to-issues` — Chia nhỏ tasks

## Preferences
- Luôn dùng tiếng Việt trong phản hồi
- Caveman mode: cắt giảm ~75% tokens
- Git: tạo commit mới, không amend (trừ khi user yêu cầu)
- Không dùng `Dism`, `sfc /scannow` (AtlasOS blocked)

## Bài học vàng (sau rollback 2026-05-08)
1. **Code tốt ≠ User hài lòng:** 31/31 tests pass nhưng vẫn rollback vì quá phức tạp
2. **KISS principle:** v1.0 ổn định > v2.0 phức tạp (Google Drive API > rclone?)
3. **Demo trước khi implement:** Cho user xem plan, confirm trước khi code
4. **Hiểu đúng user:** "stdlib-only" nghĩa là dùng stdlib thật, không dùng cryptography lib
5. **TDD không cứu được requirement sai:** Tests pass nhưng user không muốn complexity
6. **Hỏi lại khi không chắc:** User nói "stdlib-only broken" → phải hỏi lại, đừng giả định
