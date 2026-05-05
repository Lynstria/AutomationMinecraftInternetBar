# Issue #3: DRY Minecraft path lookup ✅ COMPLETED

## Parent
N/A - From /improve-codebase-architecture session

## What to build
Extracted `find_minecraft_dir()` from Work.py and Upload.py into `mc_utils.py`.

## Acceptance criteria
- [x] Tạo file `mc_utils.py` chứa hàm `find_minecraft_dir()`
- [x] Work.py import và sử dụng `mc_utils.find_minecraft_dir()`
- [x] Upload.py import và sử dụng `mc_utils.find_minecraft_dir()`
- [x] Xóa code trùng lặp trong Work.py và Upload.py
- [x] Test: TDD cycle (RED-GREEN-REFACTOR) ✅
- [x] Tất cả tests pass ✅

## Blocked by
None - completed

## Labels
refactor, ready-for-agent, completed
