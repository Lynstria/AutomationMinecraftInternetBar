<#
.SYNOPSIS
    Pipeline TLauncher & Minecraft: Download/Upload phiên bản.
    Tự động tải Python portable nếu máy chưa cài Python thực sự.
.NOTES
    Repo: Lynstria/AutomationMinecraftInternetBar
#>

#Requires -RunAsAdministrator
$ErrorActionPreference = "Continue"

# ======= CẤU HÌNH =======
$downloadPyUrl        = "https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/Minecraft/Download.py"
$workPyUrl            = "https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/Minecraft/Work.py"
$defendsPyUrl         = "https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/.vscode/Defends.py"
$uploadPyUrl          = "https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/.vscode/Upload.py"
$decryptSecretsPyUrl  = "https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/.vscode/decrypt_secrets.py"

$graalvmZipDriveLink  = "https://drive.google.com/file/d/1xrxfMiLBWOS2ptPOnUClHrNXOuozid_a/view?usp=sharing"
$versionsZipDriveLink = "https://drive.google.com/file/d/1_JH04cXYbWSbhTmn3Y9jQFAf57DayWNM/view?usp=sharing"

$pythonPortableFileId = "1YyD9-wLDuFIu5Z0O38PHF9I6iIDAt5oO"
$pythonPortableZipUrl = "https://drive.google.com/uc?export=download&id=$pythonPortableFileId"
$pythonPortableFolder = "$PSScriptRoot\python_portable"
$pythonExe            = "$pythonPortableFolder\python.exe"
# =========================

function Test-Python {
    if (Test-Path $pythonExe) {
        $result = & $pythonExe -c "print('OK')" 2>&1
        if ($LASTEXITCODE -eq 0) {
            $env:Path = "$pythonPortableFolder;$env:Path"
            return $true
        }
    }
    try {
        $null = Get-Command python -ErrorAction Stop
        $result = & python -c "print('OK')" 2>&1
        if ($LASTEXITCODE -eq 0) { return $true }
    } catch {}
    return $false
}

function Download-PythonPortable {
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
        [string[]]$Arguments
    )
    $scriptContent = (Invoke-WebRequest -Uri $ScriptUrl -UseBasicParsing).Content
    $scriptB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($scriptContent))
    
    # Dùng biến môi trường để truyền base64, tránh lỗi command-line
    $env:PY_SCRIPT_B64 = $scriptB64
    $pyCode = @"
import os, sys, base64
script_b64 = os.environ['PY_SCRIPT_B64']
sys.argv = ['script.py'] + sys.argv[1:]   # bỏ qua -c và code, chỉ còn đối số thực
exec(base64.b64decode(script_b64).decode())
"@
    $cmdArgs = @("-c", $pyCode) + $Arguments
    $result = & python $cmdArgs 2>&1
    $exitCode = $LASTEXITCODE
    Remove-Item env:PY_SCRIPT_B64 -ErrorAction SilentlyContinue
    if ($exitCode -ne 0) {
        throw "Python script exited with code $exitCode. Output: $result"
    }
    return $result
}

# === Khởi tạo ===
if (-not (Test-Python)) { Download-PythonPortable }
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
    'cryptography',
    'cryptography.fernet',
    'cryptography.hazmat.primitives.hashes',
    'cryptography.hazmat.primitives.kdf.pbkdf2'
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
$checkResult = & python -c $checkLibs 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Cài đặt thư viện cần thiết..." -ForegroundColor Cyan
    & python -m pip install --quiet --trusted-host pypi.org --trusted-host files.pythonhosted.org requests psutil gdown pydrive2 pyyaml cryptography 2>&1
    $checkResult = & python -c $checkLibs 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Không thể cài đặt thư viện. Hãy kiểm tra kết nối mạng." -ForegroundColor Red
        pause
        exit 1
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
            try {
                $workScriptContent = (Invoke-WebRequest -Uri $workPyUrl -UseBasicParsing).Content
                $env:WORK_PY_B64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($workScriptContent))
            } catch {
                Write-Host "Lỗi tải Work.py" -ForegroundColor Red
                continue
            }
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

if ($host.Name -eq "ConsoleHost") {
    Write-Host "Nhấn Enter để thoát..." -ForegroundColor Yellow
    Read-Host
}
