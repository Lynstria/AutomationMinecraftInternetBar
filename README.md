# Automation Minecraft Internet Bar (v2.5)

Dự án cá nhân, tự động hóa cài đặt Minecraft (TL1) + Upload versions lên Drive (TL2).

**Không dành cho công khai hay hội nhóm khác.**

Kết hợp logic người dùng với Claude Code, vận dụng và thử nghiệm model code, ngữ cảnh và test AI model + Claude Code.

## Luồng hoạt động

**TL1 (Cài đặt cho người chơi):**
```
Main.ps1 -> Python embed -> Download.py -> Exec.py -> CustomCore.py
```

**TL2 (Upload versions):**
```
Main.ps1 -> Decode.py -> Shield.py -> Menu2.py -> Upload.py / Manager.ps1
```

## TL1: Tải & Cài đặt

1. **Main.ps1** - Menu chọn, tải Python embed, gọi tuần tự các script Python
2. **Download.py** - Tải TLauncher.exe + GraalVM.zip + versions.zip (thử lại 3 lần, hỗ trợ Drive)
3. **Exec.py** - Chạy TLauncher installer (HITL), giải nén GraalVM -> C:\Java\, cài versions vào .minecraft\
4. **CustomCore.py** - Ghi cấu hình java vào .tlauncher\

## TL2: Upload & Quản lý Versions

1. **Decode.py** - AES256 giải mã nothing.enc -> Code.txt (thông tin xác thực Drive)
2. **Shield.py** - Xác thực mã 4 số Discord
3. **Menu2.py** - Menu: Upload / Manager
4. **Upload.py** - Nén `.minecraft\versions\` thành `.minecraft\versions-YYYY-MM-DD.zip`, upload Drive (timeout 300s)
5. **Manager.ps1** - UI tương tác: di chuyển mũi tên, space chọn/bỏ chọn, output UTF-8

## Cách dùng

**Chạy trực tiếp (RAM, không cần clone):**
```powershell
irm https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/Main.ps1 | iex
```

**Chạy từ repo:**
```powershell
.\Main.ps1
```
Chọn **1** cho TL1, **2** cho TL2.

## Cấu trúc

```
AutomationMinecraftInternetBar/
├── Main.ps1                        # Điểm vào (PowerShell, UTF-8)
├── TL1/
│   ├── Download.py                  # Tải 3 file (chỉ stdlib, UTF-8)
│   ├── Exec.py                     # Cài TLauncher + thiết lập Java
│   ├── CustomCore.py               # Ghi cấu hình java
│   └── minecraft_tlauncher_java_config.json
├── TL2/
│   ├── Decode.py                   # Giải mã AES (UTF-8)
│   ├── Shield.py                   # Xác thực Discord (UTF-8)
│   ├── Menu2.py                   # Menu TL2 (UTF-8)
│   ├── Manager.ps1                # Quản lý file Drive (UTF-8, điều hướng mũi tên)
│   ├── Stage_upload/
│   │   ├── Upload.py             # Nén + upload (UTF-8, timeout 300s)
│   │   └── Manager.py           # Liệt kê file Drive -> JSON (UTF-8)
│   └── lib_pure/
│       └── aes_pure.py            # AES256 thuần Python (UTF-8)
└── docs/
    ├── planning-session-2026-05-05.md
    └── issues/
```

## Yêu cầu

- Windows 10/11
- PowerShell 5.1+ (hỗ trợ UTF-8)
- Internet (tải TLauncher, GraalVM, versions)
- Quyền cài đặt (TLauncher installer cần admin nếu UAC bật)

## Công nghệ sử dụng

- **PowerShell** - Điều phối, menu, ghi log (output UTF-8)
- **Python 3.11.9 embed** - Chạy script (chỉ stdlib, không pip, UTF-8)
- **AES256** - Giải mã thuần Python (không thư viện ngoài)
- **Google Drive API** - Upload versions qua refresh_token

## Xử lý lỗi

- Thử lại 3 lần cho mỗi file tải (Download.py)
- Dự phòng: Nếu GitHub raw 404 -> copy file local
- File tạm: `%TEMP%\python_embed\`, tùy chọn dọn dẹp trong menu
- Timeout upload: 60s -> 300s (sửa 2026-05-08)

## Trạng thái

- [x] TL1: Tải + Cài đặt + Thiết lập Java (hoàn thành 2026-05-06)
- [x] TL2: Upload versions lên Drive (hoàn thành 2026-05-08)
- [x] Manager.ps1: UTF-8 + điều hướng mũi tên + space toggle (sửa 2026-05-08)
- [x] Upload.py: Nén trực tiếp .minecraft + log upload (sửa 2026-05-08)

## Giấy phép

MIT

❤️ Made by Lynstria – because every millisecond counts.
