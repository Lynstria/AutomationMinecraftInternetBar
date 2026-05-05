# Issue #7: Fix $PSScriptRoot empty when running via irm | iex

## Parent
N/A - Critical bug from manual testing 2026-05-05

## What to build
Fix Main.ps1 to handle case when running via `irm | iex` (no physical file, $PSScriptRoot is empty).

## Acceptance criteria
- [ ] Main.ps1 detects when $PSScriptRoot is empty
- [ ] Falls back to default config values (hardcoded in Get-Config)
- [ ] Works both when run from local file and via irm | iex

## Root cause
Dòng 26: `Join-Path $PSScriptRoot 'config.yaml'`
- Khi chạy từ file vật lý: $PSScriptRoot = đường dẫn thư mục chứa Main.ps1 ✅
- Khi chạy qua `irm | iex`: script chạy từ memory, không có file vật lý → $PSScriptRoot = "" ❌

## Proposed solution
Sửa hàm Get-Config trong Main.ps1:
1. Kiểm tra $PSScriptRoot có rỗng không
2. Nếu rỗng → trả về default values ngay lập tức (không thử đọc config.yaml)
3. Nếu không rỗng → thử đọc config.yaml như bình thường

## Files affected
- Main.ps1 (hàm Get-Config, dòng 25-72)

## Labels
bug, ready-for-agent, HITL
