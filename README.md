# Automation Minecraft Internet Bar

Tự động hoá cài đặt Minecraft (TL1) cho phòng net: download TLauncher, setup Java (GraalVM), config launcher.

## Flow TL1 (Download & Setup)

```
Main.ps1 → Python embed → Download.py → Exec.py → CustomCore.py
```

1. **Main.ps1** - Menu chọn, tải Python embed, gọi tuần tự các script Python
2. **Download.py** - Tải TLauncher.exe + GraalVM.zip + versions.zip (retry 3 lần, Google Drive handler)
3. **Exec.py** - Chạy TLauncher installer (HITL), extract GraalVM → C:\Java\, cài versions vào .minecraft\
4. **CustomCore.py** - Ghi java config vào .tlauncher\

## Cách dùng

### Chạy trực tiếp (RAM, không cần clone)
```powershell
irm https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/Main.ps1 | iex
```

### Chạy từ repo
```powershell
.\Main.ps1
```
Chọn **1** để bắt đầu TL1 pipeline.

## Cấu trúc

```
AutomationMinecraftInternetBar/
├── Main.ps1                          # Entry point (PowerShell)
├── TL1/
│   ├── Download.py                     # Tải 3 files (stdlib only)
│   ├── Exec.py                        # Install TLauncher + setup Java
│   ├── CustomCore.py                  # Write java config to .tlauncher
│   └── minecraft_tlauncher_java_config.json  # Java config template
└── docs/
    ├── planning-session-2026-05-05.md
    └── issues/
```

## Yêu cầu

- Windows 10/11
- PowerShell 5.1+
- Internet (download TLauncher, GraalVM, versions)
- Quyền cài đặt (TLauncher installer cần admin prompt nếu UAC bật)

## Tech stack

- **PowerShell** - Orchestration, menu, logging (Start-Transcript)
- **Python 3.11.9 embed** - Chạy .py scripts (stdlib only, không pip)
- **Logging** - PowerShell → Desktop\mc-automation(HH-dd-MM).log, Python → same + _python.log

## xử lý lỗi

- Retry 3 lần cho mỗi file tải (Download.py)
- Fallback: Nếu GitHub raw 404 → copy local file (khi chạy từ repo)
- Temp files: `%TEMP%\python_embed\`, `%TEMP%\mc_path.txt`, `%TEMP%\mc_log_path.txt`
- Cleanup: Menu option 2 xoá hết temp + log

## Trạng thái

- [x] TL1: Download + Install + Java setup (hoàn thành 2026-05-06)
- [ ] TL2: Coming soon (Upload/Update maps)

## License

MIT
