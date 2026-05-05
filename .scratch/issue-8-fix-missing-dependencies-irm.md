# Issue #8: Fix missing Python dependencies when running via irm | iex

## Parent
N/A - Critical bug from manual testing 2026-05-05

## What to build
Fix Invoke-PythonScriptInRam to download all dependencies (crypto_utils.py, mc_utils.py, config.py) or bundle them into single files.

## Acceptance criteria
- [ ] Khi chạy `irm | iex`, tất cả Python scripts có thể chạy độc lập
- [ ] Không còn ModuleNotFoundError: No module named 'crypto_utils', 'mc_utils', 'config'
- [ ] Vẫn hỗ trợ chạy từ repo local (có đủ file .py)

## Root cause
Invoke-PythonScriptInRam chỉ download 1 script qua URL, không download dependencies:

| Script | Import | Thiếu |
|--------|--------|------|
| Work.py | `from mc_utils import find_minecraft_dir` | mc_utils.py ❌ |
| Work.py | `from config import load_config` | config.py ❌ |
| Defends.py | `from config import load_config` | config.py ❌ |
| Upload.py | `from mc_utils import find_minecraft_dir` | mc_utils.py ❌ |
| decrypt_secrets.py | `from crypto_utils import decrypt_secrets_file` | crypto_utils.py ❌ |

## Proposed solution (Recommended)
**Bundle code vào single files** - đơn giản nhất cho irm | iex:
- Defends.py: Copy code từ config.py trực tiếp vào (xóa import)
- Upload.py: Copy code từ mc_utils.py + config.py trực tiếp vào
- Work.py: Copy code từ mc_utils.py + config.py trực tiếp vào
- decrypt_secrets.py: Copy code từ crypto_utils.py trực tiếp vào

## Files affected
- Minecraft/Work.py (bundle mc_utils.py + config.py)
- .vscode/Defends.py (bundle config.py)
- .vscode/Upload.py (bundle mc_utils.py + config.py)
- .vscode/decrypt_secrets.py (bundle crypto_utils.py)

## Labels
bug, critical, HITL, ready-for-agent
