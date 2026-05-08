# CLAUDE.md - AutomationMinecraftInternetBar

## Environment
- Terminal: Alacritty trên Windows 11
- Shell: PowerShell (Alacritty mặc định)
- Nếu PowerShell lỗi: dùng Bash (POSIX syntax) thay thế
- Alacritty hỗ trợ PowerShell tốt, ưu tiên PowerShell commands

## User Preferences
- Ngôn ngữ: Tiếng Việt trong phản hồi
- Caveman mode: Active (cắt giảm ~75% tokens, fragments OK)
- Git: Tạo commit mới, không amend (trừ khi yêu cầu)
- Không dùng `Dism`, `sfc /scannow` (AtlasOS blocked)

## Project Context
- 2 pipeline: TL1 (Download + Install + Java) + TL2 (Upload maps)
- Stdlib only (Python): urllib, zipfile, json, os, shutil
- Python embed 3.11.9 (stdlib only, no pip)
- Google Drive downloads: cần handle virus warning page
- Download order: Tlauncher → GraalVM (~800MB) → versions (~1.4GB)

## Architecture
- Main.ps1: Orchestrator, download repo + python_embed, menu TL1/TL2
- TL1/Download.py: Download 3 files, ghi mc_path.txt
- TL1/Exec.py: Install + Java setup
- TL1/CustomCore.py: Post-install config
- TL2/nothing.enc: AES encrypted data
- TL2/Decode.py + Shield.py: Decrypt + Discord auth
- TL2/Menu2.py: Upload interface

## Recent Changes (2026-05-08)
- Fix logging: Xóa Start-Transcript, remove logger từ Download.py
- Add $env:PYTHONUNBUFFERED=1 cho realtime Python stdout
- Add repo cache check (skip download nếu essential files exist)
- Modify Keep/Delete: Keep=giữ temp files, Delete=xóa tất cả
- TDD: 4 tests pass

## Skills Used
- `/caveman` - Ultra-compressed communication
- `/remember` - Read docs/ context
- `/diagnose` - Debug logging issue
- `/grill-me` - Stress-test plan
- `/tdd` - Test-driven development
