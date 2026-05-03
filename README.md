# 🎮 AutomationMinecraftInternetBar

<p align="center">
  <img src="https://img.shields.io/badge/version-2.1-blue?style=flat-square" alt="phien bản" />
  <img src="https://img.shields.io/badge/platform-Windows%2010%2B-lightgrey?style=flat-square" alt="hệ điều hành" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="giấy phép" />
  <img src="https://img.shields.io/badge/automation-100%25-brightgreen?style=flat-square" alt="tự động hóa" />
</p>

> **Pipeline tự động hoá toàn diện** cho việc cài đặt TLauncher, thiết lập Java, phiên bản Minecraft và upload/backup phiên bản lên Google Drive.
> **Tất cả chỉ bằng một dòng lệnh PowerShell.** Không cần cài đặt Python thủ công.

---

## 🧠 Tổng quan

Repo này cung cấp một hệ thống **tự động hoá thông minh** (AI‑assisted automation) được xây dựng trên PowerShell và Python, chạy trực tiếp từ RAM mà không để lại dấu vết file script. Các tính năng chính:

- **Nhánh 1 – Cài đặt**
  Tải TLauncher, GraalVM và phiên bản Minecraft từ Google Drive về máy, tự động chạy installer, chờ người dùng cài đặt xong rồi giải nén và di chuyển các file vào đúng thư mục TLauncher.

- **Nhánh 2 – Upload phiên bản**
  Nén thư mục `versions` Minecraft, upload lên Google Drive vào thư mục `Minecraft_Map`, giữ lại phiên bản cũ (đổi tên theo timestamp). Quá trình được bảo vệ bởi **ba lớp xác thực**:
  1. Mật khẩu giải mã file `secrets.enc` (AES‑256)
  2. OTP động gửi qua Discord Webhook (thay đổi mỗi 15 giây)
  3. Google OAuth 2.0

- **Python portable tự động**
  Nếu máy chưa có Python, pipeline sẽ tự tải Python portable (đã tích hợp sẵn đầy đủ thư viện) từ Google Drive của bạn và sử dụng nó để chạy các script Python.

---

## 📁 Cấu trúc repo

```
AutomationMinecraftInternetBar/
├── Main.ps1                                    # Pipeline chính (PowerShell)
├── Minecraft/
│   └── Work.py                                 # Xử lý cài đặt & di chuyển file
├── .vscode/
│   ├── Defends.py                              # Xác thực OTP qua Discord
│   ├── Upload.py                               # Nén và upload phiên bản lên Drive
│   └── decrypt_secrets.py                      # Giải mã secrets (webhook + OAuth)
├── secrets.enc                                  # File mã hoá chứa Discord Webhook & credentials Google
└── encrypt_secrets.py (tại C:\Users\Lynstria\Downloads)
                                                    # Script tạo secrets.enc mới (salt ngẫu nhiên)
```

> **Ghi chú:** File `client_secrets.json` (bản rõ) **không bao giờ** được commit. Thay vào đó, nó được mã hoá trong `secrets.enc`.

---

## 🚀 Bắt đầu nhanh

Mở **PowerShell với quyền Administrator** và chạy:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
irm https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/Main.ps1 | iex
```

---

## 🔑 Bảo mật & AI Logic

### 🔐 Lớp 1 – AES‑256
File `secrets.enc` được tạo ra bằng `encrypt_secrets.py`. Nó chứa Discord Webhook URL và Google OAuth credentials đã được mã hoá với mật khẩu do bạn đặt.
- **Định dạng mới:** Salt ngẫu nhiên 16-byte được ghi ở đầu file, giúp tăng cường bảo mật.
- **Tương thích ngược:** Vẫn giải mã được file `secrets.enc` cũ (dùng fixed salt).
- Nếu nhập sai mật khẩu, pipeline sẽ hiển thị "Sai mã API" (thông báo giả để đánh lừa kẻ tấn công).

### 🔢 Lớp 2 – OTP thông minh (AI‑driven OTP)
Script `Defends.py` tạo mã OTP bằng cách hoán vị ngẫu nhiên các chữ số của một chuỗi bí mật (`OTP_SECRET`).
- Mã này được gửi qua Discord Webhook mỗi 15 giây.
- Người dùng phải nhập đúng mã hiện tại trong khoảng thời gian đó.
- Sử dụng `secrets.SystemRandom()` để xáo trộn (cryptographically secure).
- **Lưu ý:** `OTP_SECRET` nên được set qua biến môi trường trước khi chạy:
  ```powershell
  $env:OTP_SECRET = "your_secret_here"
  ```

### ☁️ Lớp 3 – Google OAuth 2.0
Sau khi qua hai lớp trên, Google credentials được giải mã vào file tạm và sử dụng để upload lên Drive. File tạm sẽ bị xoá sau khi upload hoàn tất.

---

## 🧪 Tự động phát hiện & thich nghi

- Tự động tìm đúng thư mục Downloads của người dùng.
- Fallback tìm thư mục `.minecraft` nếu không có `.tlauncher/legacy`.
- Tự động tải Python portable nếu máy chưa cài Python.
- Tìm động thư mục GraalVM sau giải nén (không hardcode).

---

## ⚙️ Cài đặt nâng cao (dành cho nhà phát triển)

### 1. Tạo file mã hoá `secrets.enc` mới (khuyên dùng):
```powershell
cd C:\Users\Lynstria\Downloads
D:\RepoGithub\AutomationMinecraftInternetBar\.venv\Scripts\python.exe encrypt_secrets.py
```
Sau đó copy file `secrets.enc` vừa tạo vào repo `D:\RepoGithub\AutomationMinecraftInternetBar\secrets.enc`.

### 2. Thiết lập .venv cho repo:
```powershell
cd D:\RepoGithub\AutomationMinecraftInternetBar
C:\Python314\python.exe -m venv .venv
.\.venv\Scripts\pip.exe install requests psutil gdown pydrive2 pyyaml cryptography
```

### 3. Sửa các biến cấu hình trong `Main.ps1`:
- `$pythonPortableFileId`: ID file Google Drive chứa Python portable.
- `$graalvmFileId` và `$versionsFileId`: ID file GraalVM và versions.zip.

---

## ⚠️ Lưu ý quan trọng

- Chỉ sử dụng cho mục đích hợp pháp – đây là công cụ hỗ trợ quản lý phiên bản Minecraft của chính bạn.
- Không chia sẻ file `secrets.enc` hoặc mật khẩu giải mã cho bất kỳ ai.
- Sau khi tạo `client_secrets.json` mới, hãy huỷ OAuth credentials cũ trên Google Cloud Console nếu chúng đã từng bị lộ.
- **KHÔNG bao giờ gửi mật khẩu hoặc file `secrets.enc` cho bất kỳ ai (kể cả AI).**

---

## 🤖 Công nghệ sử dụng

- PowerShell 5.1+
- Python 3.14+ (embeddable portable)
- `gdown`, `pydrive2`, `cryptography`, `requests`, `psutil`
- Google Drive API v3
- Discord Webhook API
- AES‑256 (Fernet) từ thư viện `cryptography`

---

<p align="center"> <sub>Made with ❤️ by Lynstria – Automated with AI logic</sub> </p>
