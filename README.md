# Automation Minecraft Internet Bar (v2.4)

Auto setup Minecraft (TL1) + Upload versions to Drive (TL2) for net cafe.

## Flow

**TL1 (Player setup):**
```
Main.ps1 -> Python embed -> Download.py -> Exec.py -> CustomCore.py
```

**TL2 (Upload versions):**
```
Main.ps1 -> Decode.py -> Shield.py -> Menu2.py -> Upload.py / Manager.ps1
```

## TL1: Download & Setup

1. **Main.ps1** - Menu, dl Python embed, call Python scripts
2. **Download.py** - DL TLauncher.exe + GraalVM.zip + versions.zip (retry 3x, Drive handler)
3. **Exec.py** - Run TLauncher installer (HITL), extract GraalVM -> C:\Java\, install versions
4. **CustomCore.py** - Write java config to .tlauncher\

## TL2: Upload & Manage Versions

1. **Decode.py** - AES256 decrypt nothing.enc -> Code.txt (Drive creds)
2. **Shield.py** - Discord 4-digit code verification
3. **Menu2.py** - Menu: Upload / Manager
4. **Upload.py** - Zip `.minecraft\versions\` to `.minecraft\versions-YYYY-MM-DD.zip`, upload to Drive (300s timeout)
5. **Manager.ps1** - Interactive UI: arrow nav, space toggle, UTF-8 output

## Quick start

**Run directly (RAM, no clone):**
```powershell
irm https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/Main.ps1 | iex
```

**Run from repo:**
```powershell
.\Main.ps1
```
Choose **1** for TL1, **2** for TL2.

## Structure

```
AutomationMinecraftInternetBar/
├── Main.ps1                        # Entry (PS, UTF-8)
├── TL1/
│   ├── Download.py                  # DL 3 files (stdlib only, UTF-8)
│   ├── Exec.py                     # Install TLauncher + Java
│   ├── CustomCore.py               # Write java config
│   └── minecraft_tlauncher_java_config.json
├── TL2/
│   ├── Decode.py                   # AES decrypt (UTF-8)
│   ├── Shield.py                   # Discord verify (UTF-8)
│   ├── Menu2.py                   # TL2 menu (UTF-8)
│   ├── Manager.ps1                # Drive file manager (UTF-8, arrow nav)
│   ├── Stage_upload/
│   │   ├── Upload.py             # Zip + upload (UTF-8, 300s timeout)
│   │   └── Manager.py           # List Drive files -> JSON (UTF-8)
│   └── lib_pure/
│       └── aes_pure.py            # AES256 pure Python (UTF-8)
└── docs/
    ├── planning-session-2026-05-05.md
    └── issues/
```

## Requirements

- Windows 10/11
- PowerShell 5.1+ (UTF-8 support)
- Internet (DL TLauncher, GraalVM, versions)
- Admin for TLauncher installer (UAC)

## Tech stack

- **PowerShell** - Orchestration, menu, logging (UTF-8 output)
- **Python 3.11.9 embed** - Scripts (stdlib only, no pip, UTF-8)
- **AES256** - Pure Python decrypt (no external lib)
- **Google Drive API** - Upload versions via refresh_token

## Error handling

- Retry 3x per download (Download.py)
- Fallback: GitHub raw 404 -> copy local file
- Temp: `%TEMP%\python_embed\`, cleanup option in menu
- Upload timeout: 60s -> 300s (fixed 2026-05-08)

## Status

- [x] TL1: Download + Install + Java setup (done 2026-05-06)
- [x] TL2: Upload versions to Drive (done 2026-05-08)
- [x] Manager.ps1: UTF-8 + arrow nav + space toggle (fixed 2026-05-08)
- [x] Upload.py: Direct zip to .minecraft + upload log (fixed 2026-05-08)

## License

MIT
