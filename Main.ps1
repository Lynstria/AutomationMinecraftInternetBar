<#
.SYNOPSIS
    Pipeline TLauncher & Minecraft: Download/Upload phiên bản.
    Tất cả file được tải bằng PowerShell, không phụ thuộc gdown.
.NOTES
    Repo: Lynstria/AutomationMinecraftInternetBar
#>

#Requires -RunAsAdministrator
$ErrorActionPreference = "Continue"

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

# ======= CẤU HÌNH =======
# Chỉ dùng Work.py và các script nhánh 2
$cacheBust = "?t=" + (Get-Date -Format "yyyyMMddHHmmss")
$workPyUrl            = "https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/Minecraft/Work.py" + $cacheBust
$defendsPyUrl         = "https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/.vscode/Defends.py" + $cacheBust
$uploadPyUrl          = "https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/.vscode/Upload.py" + $cacheBust
$decryptSecretsPyUrl  = "https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/.vscode/decrypt_secrets.py" + $cacheBust

# Link Google Drive – dùng ID để tạo direct link
$graalvmFileId  = "1xrxfMiLBWOS2ptPOnUClHrNXOuozid_a"
$versionsFileId = "1_JH04cXYbWSbhTmn3Y9jQFAf57DayWNM"
$tlauncherUrl   = "https://dl1.tlauncher.org/f.php?f=files%2FTLauncher-Installer-1.9.5.1.exe"

$pythonPortableFileId = "1YyD9-wLDuFIu5Z0O38PHF9I6iIDAt5oO"
$pythonPortableZipUrl = "https://drive.google.com/uc?export=download&id=$pythonPortableFileId"
$pythonPortableFolder = "$PSScriptRoot\python_portable"
$pythonExe            = "$pythonPortableFolder\python.exe"
# =========================

function Test-Python {
    if (Test-Path $pythonExe) {
        $null = & $pythonExe -c "print('OK')" 2>&1
        if ($LASTEXITCODE -eq 0) {
            $env:Path = "$pythonPortableFolder;$env:Path"
            return $true
        }
    }
    try {
        $null = Get-Command python -ErrorAction Stop
        $null = & python -c "print('OK')" 2>&1
        if ($LASTEXITCODE -eq 0) { return $true }
    } catch {}
    return $false
}

function Get-PythonPortable {
    Write-Host "Không tìm thấy Python. Đang tải Python portable từ Google Drive..." -ForegroundColor Yellow
    $tempZip = "$env:TEMP\python_portable.zip"
    try {
        (New-Object System.Net.WebClient).DownloadFile($pythonPortableZipUrl, $tempZip)
        Write-Host "Đã tải xong. Đang giải nén..." -ForegroundColor Yellow
        Expand-Archive -Path $tempZip -DestinationPath $pythonPortableFolder -Force
        Remove-Item $tempZip
        $env:Path = "$pythonPortableFolder;$env:Path"
        Write-Host "Python portable đã sẵn sàng." -ForegroundColor Green
    } catch {
        Write-Host "Lỗi khi tải Python portable: $_" -ForegroundColor Red
        pause
        exit 1
    }
}

function Invoke-PythonScriptInRam {
    param(
        [string]$ScriptUrl,
        [string[]]$Arguments,
        [switch]$Interactive
    )
    $scriptContent = (Invoke-WebRequest -Uri $ScriptUrl -UseBasicParsing).Content
    $scriptB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($scriptContent))

    $env:PY_SCRIPT_B64 = $scriptB64
    $pyCode = @"
import os, sys, base64
script_b64 = os.environ['PY_SCRIPT_B64']
sys.argv = ['script.py'] + sys.argv[1:]
exec(base64.b64decode(script_b64).decode())
"@
    $cmdArgs = @("-c", $pyCode) + $Arguments

    if ($Interactive) {
        # Chạy tương tác - không capture output
        & python $cmdArgs 2>&1
        $exitCode = $LASTEXITCODE
    } else {
        $result = & python $cmdArgs 2>&1
        $exitCode = $LASTEXITCODE
        Remove-Item env:PY_SCRIPT_B64 -ErrorAction SilentlyContinue
        if ($exitCode -ne 0) {
            throw "Python script exited with code $exitCode. Output: $result"
        }
        return $result
    }

    Remove-Item env:PY_SCRIPT_B64 -ErrorAction SilentlyContinue
    if ($exitCode -ne 0) {
        throw "Python script exited with code $exitCode."
    }
}

# === Khởi tạo ===
if (-not (Test-Python)) { Get-PythonPortable }
else { Write-Host "Đã tìm thấy Python." -ForegroundColor Cyan }

# Kiểm tra và cài thư viện
$checkLibs = @"
import importlib, sys
libs = [
    'requests',
    'psutil',
    'gdown',
    'pydrive2',
    'yaml',
    'cryptography'
]
missing = []
for lib in libs:
    try:
        importlib.import_module(lib)
    except:
        missing.append(lib)
if missing:
    print('MISSING:' + ','.join(missing))
    sys.exit(1)
print('OK')
"@
$null = & python -c $checkLibs 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Cài đặt thư viện cần thiết..." -ForegroundColor Cyan
    & python -m pip install --quiet --trusted-host pypi.org --trusted-host files.pythonhosted.org requests psutil gdown pydrive2 pyyaml cryptography 2>&1
    $null = & python -c $checkLibs 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Không thể cài đặt thư viện. Hãy kiểm tra kết nối mạng." -ForegroundColor Red
        pause
        exit 1
    }
}

# Hàm tải file từ Google Drive (xử lý confirm nếu file lớn)
function Get-DriveFile {
    param(
        [string]$FileId,
        [string]$Destination
    )
    $url = "https://drive.google.com/uc?export=download&id=$FileId"
    try {
        # Sử dụng Invoke-WebRequest với session để xử lý cookie
        $session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
        $session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

        # Lần 1: Lấy trang xác nhận (nếu có)
        $response = Invoke-WebRequest -Uri $url -Method Get -WebSession $session -UseBasicParsing

        # Kiểm tra nếu có trang xác nhận (file lớn)
        if ($response.Content -match 'confirm=([^&"]+)') {
            $confirmCode = $Matches[1]
            $downloadUrl = "https://drive.google.com/uc?export=download&confirm=$confirmCode&id=$FileId"
            $response = Invoke-WebRequest -Uri $downloadUrl -Method Get -WebSession $session -UseBasicParsing
        }

        # Lưu nội dung vào file
        [System.IO.File]::WriteAllBytes($Destination, $response.Content)
        Write-Host "[+] Đã tải: $Destination"
    } catch {
        throw "Không thể tải file từ Google Drive: $_"
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
            $downloadsDir = [Environment]::GetFolderPath("UserProfile") + "\Downloads"
            $tlauncherExe = "$downloadsDir\TLauncher-Installer-1.9.5.1.exe"
            $graalvmZip   = "$downloadsDir\graalvm-jdk-17.0.12_windows-x64_bin.zip"
            $versionsZip  = "$downloadsDir\versions.zip"

            try {
                # 1. Tải TLauncher (luôn tải, không kiểm tra tồn tại)
                Write-Host "[1/3] Đang tải TLauncher..." -ForegroundColor Cyan
                $wc = New-Object System.Net.WebClient
                $wc.Headers.Add("User-Agent", "Mozilla/5.0")
                $wc.DownloadFile($tlauncherUrl, $tlauncherExe)
                Write-Host "[+] TLauncher đã tải xong." -ForegroundColor Green

                # 2. Tải GraalVM zip
                Write-Host "[2/3] Đang tải GraalVM..." -ForegroundColor Cyan
                Get-DriveFile -FileId $graalvmFileId -Destination $graalvmZip

                # 3. Tải versions.zip
                Write-Host "[3/3] Đang tải Versions..." -ForegroundColor Cyan
                Get-DriveFile -FileId $versionsFileId -Destination $versionsZip

                Write-Host "[✅] Đã tải đủ 3 file. Bắt đầu cài đặt..." -ForegroundColor Green

                # Gọi Work.py
                Invoke-PythonScriptInRam -ScriptUrl $workPyUrl
                Write-Host "Nhánh 1 hoàn tất." -ForegroundColor Green
            } catch {
                Write-Host "Lỗi nhánh 1: $_" -ForegroundColor Red
            }
        }
        '2' {
            Write-Host "Bắt đầu nhánh 2: Upload phiên bản Minecraft..." -ForegroundColor Green
            try {
                $output = Invoke-PythonScriptInRam -ScriptUrl $decryptSecretsPyUrl
                foreach ($line in $output) {
                    if ($line -match "^DISCORD_WEBHOOK_URL=(.+)$") {
                        $env:DISCORD_WEBHOOK_URL = $Matches[1]
                    }
                    if ($line -match "^GOOGLE_CREDENTIALS_PATH=(.+)$") {
                        $env:GOOGLE_CREDENTIALS_PATH = $Matches[1]
                    }
                }
                Write-Host "[✅] Secrets đã sẵn sàng." -ForegroundColor Green
                Invoke-PythonScriptInRam -ScriptUrl $defendsPyUrl -Interactive
                Write-Host "[✅] Xác thực OTP thành công." -ForegroundColor Green
                Invoke-PythonScriptInRam -ScriptUrl $uploadPyUrl
                Write-Host "[✅] Upload hoàn tất." -ForegroundColor Green
            } catch {
                Write-Host "Lỗi nhánh 2: $_" -ForegroundColor Red
            } finally {
                if ($env:GOOGLE_CREDENTIALS_PATH) {
                    Remove-Item $env:GOOGLE_CREDENTIALS_PATH -Force -ErrorAction SilentlyContinue
                }
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

if ($host.Name -eq "ConsoleHost") {
    Write-Host "Nhấn Enter để thoát..." -ForegroundColor Yellow
    Read-Host
}
