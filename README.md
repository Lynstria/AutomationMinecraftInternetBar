# 🎮 AutomationMinecraftInternetBar

<p align="center">
  <img src="https://img.shields.io/badge/version-2.0-blue?style=flat-square" alt="phiên bản" />
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
  Nếu máy chưa cài Python, pipeline sẽ tự tải Python portable (đã tích hợp sẵn đầy đủ thư viện) từ Google Drive của bạn và sử dụng nó để chạy các script Python.

---

## 📁 Cấu trúc repo
```
AutomationMinecraftInternetBar/
├── Main.ps1 # Pipeline chính (PowerShell)
├── Minecraft/
│ ├── Download.py # Tải file cài đặt
│ └── Work.py # Xử lý cài đặt & di chuyển file
├── .vscode/
│ ├── Defends.py # Xác thực OTP qua Discord
│ ├── Upload.py # Nén và upload phiên bản lên Drive
│ └── decrypt_secrets.py # Giải mã secrets (webhook + OAuth)
└── secrets.enc # File mã hoá chứa Discord Webhook & credentials Google (được phép commit)
```

> **Ghi chú:** File `client_secrets.json` (bản rõ) **không bao giờ** được commit. Thay vào đó, nó được mã hoá trong `secrets.enc`.

---

## 🚀 Bắt đầu nhanh

Mở **PowerShell với quyền Administrator** và chạy:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
irm https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/Main.ps1 | iex
```
🔐 Bảo mật & AI Logic
🔑 Lớp 1 – AES‑256
File secrets.enc được tạo ra bằng encrypt_secrets.py. Nó chứa Discord Webhook URL và Google OAuth credentials đã được mã hoá với mật khẩu do bạn đặt. Nếu nhập sai mật khẩu, pipeline sẽ hiển thị “Sai mã API” (thông báo giả để đánh lừa kẻ tấn công).

🔢 Lớp 2 – OTP thông minh (AI‑driven OTP)
Script Defends.py tạo mã OTP bằng cách hoán vị ngẫu nhiên các chữ số của một chuỗi bí mật. Mã này được gửi qua Discord Webhook mỗi 15 giây. Người dùng phải nhập đúng mã hiện tại trong khoảng thời gian đó.
Đây là một dạng AI‑generated time‑based OTP – không dùng thuật toán TOTP chuẩn mà dùng hoán vị ngẫu nhiên để tránh các công cụ dò đoán.

☁️ Lớp 3 – Google OAuth 2.0
Sau khi qua hai lớp trên, Google credentials được giải mã vào file tạm và sử dụng để upload lên Drive. File tạm sẽ bị xoá sau khi upload hoàn tất.

🧪 Tự động phát hiện & thích nghi
Tự động tìm đúng thư mục Downloads của người dùng.

Fallback tìm thư mục .minecraft nếu không có .tlauncher/legacy.

Tự động tải Python portable nếu máy chưa cài Python.

⚙️ Cài đặt nâng cao (dành cho nhà phát triển)

1. Tạo file mã hoá secrets.enc:
    ```
    python encrypt_secrets.py
    ```
2. Tạo Python portable riêng:
    Xem hướng dẫn trong Wiki (nếu có).

3. Sửa các biến cấu hình trong Main.ps1:

    $pythonPortableFileId: ID file Google Drive chứa Python portable (nếu muốn dùng file riêng).

    $graalvmZipDriveLink và $versionsZipDriveLink: liên kết tải cho nhánh 1.

⚠️ Lưu ý quan trọng
    Chỉ sử dụng cho mục đích hợp pháp – đây là công cụ hỗ trợ quản lý phiên bản Minecraft của chính bạn.

    Không chia sẻ file secrets.enc hoặc mật khẩu giải mã cho bất kỳ ai.

    Sau khi tạo client_secrets.json mới, hãy huỷ OAuth credentials cũ trên Google Cloud Console nếu chúng đã từng bị lộ.

🤖 Công nghệ sử dụng
    PowerShell 5.1+

    Python 3.10+ (embeddable portable)

    gdown, pydrive2, cryptography, requests, psutil

    Google Drive API v3

    Discord Webhook API

    AES‑256 (Fernet) từ thư viện cryptography

<p align="center"> <sub>Made with ❤️ by Lynstria – Automated with AI logic</sub> </p>