<#
.SYNOPSIS
    Pipeline TLauncher & Minecraft: Download/Upload phiên bản.
.NOTES
    Repo: Lynstria/AutomationMinecraftInternetBar
#>

#Requires -RunAsAdministrator
$ErrorActionPreference = "Stop"

# ======= CẤU HÌNH =======
# Raw URL của các file .py trong repo của bạn
$downloadPyUrl = "https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/Minecraft/Download.py"
$workPyUrl     = "https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/Minecraft/Work.py"
$defendsPyUrl  = "https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/.vscode/Defends.py"
$uploadPyUrl   = "https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/.vscode/Upload.py"

# Link Google Drive cố định (cho nhánh 1)
$graalvmZipDriveLink = "https://drive.google.com/file/d/1xrxfMiLBWOS2ptPOnUClHrNXOuozid_a/view?usp=sharing"
$versionsZipDriveLink = "https://drive.google.com/file/d/1_JH04cXYbWSbhTmn3Y9jQFAf57DayWNM/view?usp=sharing"
# =========================

function Test-Python {
    try {
        $null = Get-Command python -ErrorAction Stop
    } catch {
        Write-Host "Python chưa được cài đặt hoặc không có trong PATH." -ForegroundColor Red
        exit 1
    }
}

function Invoke-PythonScriptInRam {
    param(
        [string]$ScriptUrl,
        [string[]]$Arguments
    )
    $scriptContent = (Invoke-WebRequest -Uri $ScriptUrl -UseBasicParsing).Content
    $scriptB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($scriptContent))
    $cmdArgs = @("-c", "import base64, sys; exec(base64.b64decode(sys.argv[1]).decode())", $scriptB64) + $Arguments
    $proc = Start-Process -FilePath "python" -ArgumentList $cmdArgs -NoNewWindow -Wait -PassThru
    if ($proc.ExitCode -ne 0) {
        throw "Python script exited with code $($proc.ExitCode)"
    }
}

# Đảm bảo thư viện
Test-Python
Write-Host "Cài đặt thư viện Python cần thiết..." -ForegroundColor Cyan
pip install requests psutil gdown pydrive2 pyyaml 2>$null

# Kiểm tra biến môi trường DISCORD_WEBHOOK_URL (cần cho nhánh 2)
if (-not $env:DISCORD_WEBHOOK_URL) {
    Write-Host "[!] Cảnh báo: Biến môi trường DISCORD_WEBHOOK_URL chưa được thiết lập." -ForegroundColor Yellow
    $confirm = Read-Host "Bạn có muốn nhập thủ công không? (y/n)"
    if ($confirm -eq 'y') {
        $env:DISCORD_WEBHOOK_URL = Read-Host "Dán Discord Webhook URL"
    } else {
        Write-Host "Nhánh 2 sẽ không hoạt động nếu không có webhook." -ForegroundColor Red
    }
}

# Menu
do {
    Write-Host "`n=== PIPELINE MENU ===" -ForegroundColor Yellow
    Write-Host "1. Tải và cài đặt TLauncher + Minecraft (Download & Work)"
    Write-Host "2. Upload phiên bản Minecraft lên Google Drive (Defends & Upload)"
    Write-Host "3. Thoát"
    $choice = Read-Host "Nhập lựa chọn (1/2/3)"

    switch ($choice) {
        '1' {
            Write-Host "Bắt đầu nhánh 1: Tải xuống và cài đặt..." -ForegroundColor Green
            # Lấy nội dung Work.py để truyền qua biến môi trường
            $workScriptContent = (Invoke-WebRequest -Uri $workPyUrl -UseBasicParsing).Content
            $env:WORK_PY_B64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($workScriptContent))
            try {
                Invoke-PythonScriptInRam -ScriptUrl $downloadPyUrl -Arguments @("--graalvm-url", $graalvmZipDriveLink, "--versions-url", $versionsZipDriveLink)
                Write-Host "Nhánh 1 hoàn tất." -ForegroundColor Green
            } catch {
                Write-Host "Lỗi nhánh 1: $_" -ForegroundColor Red
            } finally {
                Remove-Item env:WORK_PY_B64 -ErrorAction SilentlyContinue
            }
        }
        '2' {
            if (-not $env:DISCORD_WEBHOOK_URL) {
                Write-Host "Nhánh 2 yêu cầu Discord Webhook. Vui lòng thiết lập biến môi trường DISCORD_WEBHOOK_URL." -ForegroundColor Red
                continue
            }
            Write-Host "Bắt đầu nhánh 2: Xác thực OTP và upload..." -ForegroundColor Green
            try {
                Invoke-PythonScriptInRam -ScriptUrl $defendsPyUrl
                Write-Host "Xác thực thành công, bắt đầu upload..." -ForegroundColor Green
                Invoke-PythonScriptInRam -ScriptUrl $uploadPyUrl
                Write-Host "Upload hoàn tất." -ForegroundColor Green
            } catch {
                Write-Host "Lỗi nhánh 2: $_" -ForegroundColor Red
            }
        }
        '3' {
            Write-Host "Thoát." -ForegroundColor Yellow
            break
        }
        default {
            Write-Host "Lựa chọn không hợp lệ." -ForegroundColor Red
        }
    }
} while ($choice -ne '3')