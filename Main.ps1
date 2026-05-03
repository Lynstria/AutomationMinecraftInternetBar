<#
.SYNOPSIS
    Pipeline TLauncher & Minecraft: Download/Upload phiên bản.
    Tự động tải Python portable nếu máy chưa cài Python.
.NOTES
    Repo: Lynstria/AutomationMinecraftInternetBar
#>

#Requires -RunAsAdministrator
$ErrorActionPreference = "Stop"

# ======= CẤU HÌNH =======
# Raw URL các file .py
$downloadPyUrl        = "https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/Minecraft/Download.py"
$workPyUrl            = "https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/Minecraft/Work.py"
$defendsPyUrl         = "https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/.vscode/Defends.py"
$uploadPyUrl          = "https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/.vscode/Upload.py"
$decryptSecretsPyUrl  = "https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/.vscode/decrypt_secrets.py"

# Link Google Drive cố định (cho nhánh 1)
$graalvmZipDriveLink  = "https://drive.google.com/file/d/1xrxfMiLBWOS2ptPOnUClHrNXOuozid_a/view?usp=sharing"
$versionsZipDriveLink = "https://drive.google.com/file/d/1_JH04cXYbWSbhTmn3Y9jQFAf57DayWNM/view?usp=sharing"

# Python portable (file zip bạn đã upload)
$pythonPortableFileId  = "1YyD9-wLDuFIu5Z0O38PHF9I6iIDAt5oO"
$pythonPortableZipUrl  = "https://drive.google.com/uc?export=download&id=$pythonPortableFileId"
$pythonPortableFolder  = "$PSScriptRoot\python_portable"
$pythonExe             = "$pythonPortableFolder\python.exe"
# =========================

function Test-Python {
    # Ưu tiên Python hệ thống
    try {
        $null = Get-Command python -ErrorAction Stop
        return $true
    } catch {}
    # Kiểm tra Python portable đã giải nén sẵn
    if (Test-Path $pythonExe) {
        $env:Path = "$pythonPortableFolder;$env:Path"
        return $true
    }
    return $false
}

function Download-PythonPortable {
    Write-Host "Không tìm thấy Python. Đang tải Python portable từ Google Drive..." -ForegroundColor Yellow
    Write-Host "Dung lượng khoảng 40-50MB, vui lòng chờ..." -ForegroundColor Yellow
    $tempZip = "$env:TEMP\python_portable.zip"
    try {
        $webClient = New-Object System.Net.WebClient
        $webClient.DownloadFile($pythonPortableZipUrl, $tempZip)
        Write-Host "Đã tải xong. Đang giải nén..." -ForegroundColor Yellow
        Expand-Archive -Path $tempZip -DestinationPath $pythonPortableFolder -Force
        Remove-Item $tempZip
        $env:Path = "$pythonPortableFolder;$env:Path"
        Write-Host "Python portable đã sẵn sàng." -ForegroundColor Green
    } catch {
        Write-Host "Lỗi khi tải Python portable: $_" -ForegroundColor Red
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
    $result = & python $cmdArgs 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python script exited with code $LASTEXITCODE. Output: $result"
    }
    return $result
}

# Khởi tạo Python
if (-not (Test-Python)) {
    Download-PythonPortable
} else {
    Write-Host "Đã tìm thấy Python." -ForegroundColor Cyan
}

# Kiểm tra và cài thư viện nếu cần
$checkLibs = @"
import importlib, sys
libs = ['requests','psutil','gdown','pydrive2','yaml','cryptography','fernet']
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
$checkResult = & python -c $checkLibs 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Cài đặt thư viện cần thiết..." -ForegroundColor Cyan
    & python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org requests psutil gdown pydrive2 pyyaml cryptography 2>$null
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
                Invoke-PythonScriptInRam -ScriptUrl $defendsPyUrl
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