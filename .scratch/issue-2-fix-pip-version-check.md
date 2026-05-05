# Issue #2: Suppress pip version check noise

## Parent
N/A - Root issue from /diagnose session

## What to build
Thêm `--disable-pip-version-check` vào lệnh pip install trong Main.ps1 để tránh thông báo cập nhật pip gây NativeCommandError trong PowerShell.

## Acceptance criteria
- [ ] Main.ps1 dòng 203 có cờ `--disable-pip-version-check`
- [ ] Pip install chạy không in thông báo "A new release of pip is available" ra stderr
- [ ] Không còn NativeCommandError khi cài thư viện

## Blocked by
None - can start immediately

## Labels
bug, ready-for-agent
