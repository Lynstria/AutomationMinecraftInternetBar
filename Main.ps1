<#
.SYNOPSIS
    Pipeline tự động tải, cài TLauncher và thiết lập Java/Minecraft.
.DESCRIPTION
    Tải Download.py và Work.py từ GitHub, thực thi trong RAM.
    Yêu cầu quyền Administrator để ghi vào C:\download và C:\Java.
.NOTES
    Thay đổi $downloadPyUrl, $workPyUrl thành raw URL thực tế trên GitHub của bạn.
#>

#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

# ======= CẤU HÌNH =======
# Thay thế bằng raw URL của chính bạn trên GitHub
$downloadPyUrl = "https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/Minecraft/Download.py"
$workPyUrl     = "https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/Minecraft/Work.py"

# Link Google Drive đã cung cấp
$graalvmZipDriveLink = "https://drive.google.com/file/d/1xrxfMiLBWOS2ptPOnUClHrNXOuozid_a/view?usp=sharing"
$versionsZipDriveLink = "https://drive.google.com/file/d/1_JH04cXYbWSbhTmn3Y9jQFAf57DayWNM/view?usp=sharing"
# =========================

# Kiểm tra Python
try {
    $null = Get-Command python -ErrorAction Stop
} catch {
    Write-Host "Python chưa được cài đặt hoặc không có trong PATH." -ForegroundColor Red
    exit 1
}

# Cài thư viện cần thiết
Write-Host "Đảm bảo các thư viện Python cần thiết..." -ForegroundColor Cyan
pip install requests psutil gdown 2>$null

# Tải nội dung file .py từ GitHub
Write-Host "Đang tải mã nguồn từ GitHub..." -ForegroundColor Cyan
$downloadScript = (Invoke-WebRequest -Uri $downloadPyUrl -UseBasicParsing).Content
$workScript     = (Invoke-WebRequest -Uri $workPyUrl -UseBasicParsing).Content

# Mã hoá base64
$downloadB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($downloadScript))
$workB64     = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($workScript))

# Đặt biến môi trường cho Download.py để nó có thể gọi Work.py
$env:WORK_PY_B64 = $workB64

# Xây dựng câu lệnh thực thi Download.py trong RAM
$cmdArgs = @(
    "-c",
    "import base64, sys; exec(base64.b64decode(sys.argv[1]).decode())",
    $downloadB64,
    "--graalvm-url", $graalvmZipDriveLink,
    "--versions-url", $versionsZipDriveLink
)

Write-Host "Bắt đầu thực thi pipeline..." -ForegroundColor Green
$proc = Start-Process -FilePath "python" -ArgumentList $cmdArgs -NoNewWindow -Wait -PassThru
if ($proc.ExitCode -ne 0) {
    Write-Host "Pipeline kết thúc với lỗi (exit code $($proc.ExitCode))." -ForegroundColor Red
    exit $proc.ExitCode
}

Write-Host "Pipeline hoàn tất thành công!" -ForegroundColor Green