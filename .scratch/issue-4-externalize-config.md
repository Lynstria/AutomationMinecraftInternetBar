# Issue #4: Externalize hard-coded config ✅ COMPLETED

## Parent
N/A - From /improve-codebase-architecture session

## What to build
Tạo `config.yaml` và `config.py` để quản lý tất cả hard-coded values.

## Acceptance criteria
- [x] Tạo `config.yaml` với các fields: graalvm_file_id, versions_file_id, python_portable_file_id, tlauncher_url, java_dest_root, otp_timeout_seconds
- [x] Tạo `config.py` với hàm `load_config()`
- [x] Main.ps1 đọc config.yaml thay vì hard-coded variables
- [x] Defends.py đọc `otp_timeout_seconds` từ config
- [x] Work.py đọc `java_dest_root` từ config
- [x] Test: TDD cycle (RED-GREEN-REFACTOR) ✅
- [x] Tất cả tests pass ✅

## Blocked by
None - completed

## Labels
refactor, ready-for-agent, completed
