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
$REPO_RAW              = "https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main"
$tempDir               = "$env:TEMP\Automation_Bootstrap"
$workPyUrl             = "$REPO_RAW/Minecraft/Work.py"
$defendsPyUrl          = "$REPO_RAW/.vscode/Defends.py"
$uploadPyUrl           = "$REPO_RAW/.vscode/Upload.py"
$decryptSecretsPyUrl  = "$REPO_RAW/.vscode/decrypt_secrets.py"

# Link Google Drive – dùng ID để tạo direct link
$graalvmFileId  = "1xrxfMiLBWOS2ptPOnUClHrNXOuozid_a"
$versionsFileId = "1_JH04cXYbWSbhTmn3Y9jQFAf57DayWNM"
$tlauncherUrl   = "https://dl1.tlauncher.org/f.php?f=files%2FTLauncher-Installer-1.9.5.1.exe"

$pythonPortableFileId = "1YyD9-wLDuFIu5Z0O38PHF9I6iIDAt5oO"
$pythonPortableFolder = "$tempDir\python_portable"
$pythonExe            = "$pythonPortableFolder\Scripts\python.exe"
# =========================

function Test-Venv {
    $venvCandidates = @(
        if ($PSScriptRoot) {
            Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
            Join-Path $PSScriptRoot 'venv\Scripts\python.exe'
        }
        '.\.venv\Scripts\python.exe'
        '.\venv\Scripts\python.exe'
    )
    foreach ($p in $venvCandidates) {
        if (Test-Path $p) {
            $null = & $p -c "print('OK')" 2>&1
            if ($LASTEXITCODE -eq 0) {
                $script:pythonExe = (Resolve-Path $p).Path
                Write-Host "Tìm thấy venv: $pythonExe" -ForegroundColor Cyan
                return $true
            }
        }
    }
    return $false
}

function Test-PortablePython {
    if (Test-Path $pythonExe) {
        $null = & $pythonExe -c "print('OK')" 2>&1
        if ($LASTEXITCODE -eq 0) {
            $env:Path = "$pythonPortableFolder;$env:Path"
            return $true
        }
    }
    return $false
}

function New-Venv {
    param([string]$SystemPython)
    $venvDir = "$tempDir\venv"
    if (Test-Path "$venvDir\Scripts\python.exe") {
        Write-Host "Đã có sẵn venv tại $venvDir" -ForegroundColor Cyan
        $script:pythonExe = "$venvDir\Scripts\python.exe"
        return $true
    }
    Write-Host "Đang tạo venv từ $SystemPython..." -ForegroundColor Yellow
    try {
        & $SystemPython -m venv $venvDir 2>&1 | Out-Null
        if (Test-Path "$venvDir\Scripts\python.exe") {
            $script:pythonExe = "$venvDir\Scripts\python.exe"
            $env:Path = "$venvDir\Scripts;$env:Path"
            Write-Host "Venv đã sẵn sàng: $pythonExe" -ForegroundColor Green
            return $true
        }
    } catch {}
    return $false
}

function Test-Python {
    # 0. Thử venv có sẵn (nếu chạy từ repo local)
    if (Test-Venv) { return $true }

    # 1. Thử Python portable
    if (Test-PortablePython) { return $true }

    # 2. Thử Python hệ thống -> tạo venv
    try {
        $sysPython = (Get-Command python -ErrorAction Stop).Source
        $null = & $sysPython -c "print('OK')" 2>&1
        if ($LASTEXITCODE -eq 0) {
            if (New-Venv -SystemPython $sysPython) { return $true }
        }
    } catch {}

    return $false
}

function Get-PythonPortable {
    Write-Host "Không tìm thấy Python. Đang tải Python portable từ Google Drive..." -ForegroundColor Yellow
    $tempZip = "$tempDir\python_portable.zip"
    if (-not (Test-Path $tempDir)) { New-Item -ItemType Directory -Path $tempDir -Force | Out-Null }
    try {
        Get-DriveFile -FileId $pythonPortableFileId -Destination $tempZip
        Write-Host "Đã tải xong. Đang giải nén..." -ForegroundColor Yellow
        Expand-Archive -Path $tempZip -DestinationPath $pythonPortableFolder -Force
        Remove-Item $tempZip -Force -ErrorAction SilentlyContinue
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
        [string]$ScriptPath,
        [string[]]$Arguments,
        [switch]$Interactive
    )
    if (-not (Test-Path $tempDir)) { New-Item -ItemType Directory -Path $tempDir -Force | Out-Null }
    if (Test-Path $ScriptPath) {
        $scriptContent = Get-Content $ScriptPath -Raw
    } else {
        $scriptContent = (Invoke-WebRequest -Uri $ScriptPath -UseBasicParsing).Content
    }
    $tmpScript = "$tempDir\script_$(Get-Random).py"
    [System.IO.File]::WriteAllText($tmpScript, $scriptContent, [System.Text.Encoding]::UTF8)

    try {
        $cmdArgs = @($tmpScript) + $Arguments

        if ($Interactive) {
            & $pythonExe $cmdArgs 2>&1
            $exitCode = $LASTEXITCODE
        } else {
            $result = & $pythonExe $cmdArgs 2>&1
            $exitCode = $LASTEXITCODE
            if ($exitCode -ne 0) {
                throw "Python script exited with code $exitCode. Output: $result"
            }
            return $result
        }
    } finally {
        Remove-Item $tmpScript -Force -ErrorAction SilentlyContinue
    }

    if ($exitCode -ne 0) {
        throw "Python script exited with code $exitCode."
    }
}

# === Khởi tạo ===
# Dọn file .py tạm từ lần chạy trước (nếu có)
if (Test-Path $tempDir) {
    Get-ChildItem "$tempDir\script_*.py" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
}
if (-not (Test-Python)) {
    Get-PythonPortable
    # Sau khi có portable, kiểm tra lại
    if (-not (Test-PortablePython)) {
        Write-Host "Không thể khởi tạo Python." -ForegroundColor Red
        pause; exit 1
    }
}
Write-Host "Đã sẵn sàng với Python: $pythonExe" -ForegroundColor Cyan

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
$null = & $pythonExe -c $checkLibs 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Cài đặt thư viện cần thiết..." -ForegroundColor Cyan
    & $pythonExe -m pip install --no-cache-dir --quiet --trusted-host pypi.org --trusted-host files.pythonhosted.org requests psutil gdown pydrive2 pyyaml cryptography 2>&1
    $null = & $pythonExe -c $checkLibs 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Không thể cài đặt thư viện. Hãy kiểm tra kết nối mạng." -ForegroundColor Red
        pause
        exit 1
    }
}

# Kiểm tra dung lượng file tải về (phải đạt mức tối thiểu)
function Test-DownloadSize {
    param(
        [string]$FilePath,
        [long]$MinBytes,
        [string]$Label
    )
    if (-not (Test-Path $FilePath)) {
        throw "$Label không tồn tại sau khi tải: $FilePath"
    }
    $size = (Get-Item $FilePath).Length
    if ($size -lt $MinBytes) {
        $sizeMB = [math]::Round($size / 1MB, 2)
        $minMB = [math]::Round($MinBytes / 1MB, 2)
        throw "$Label quá nhỏ ($sizeMB MB), có thể tải sai. Yêu cầu tối thiểu: $minMB MB"
    }
    $sizeMB = [math]::Round($size / 1MB, 2)
    Write-Host "[+] $Label dung lượng OK: $sizeMB MB"
}

# Hàm tải file từ Google Drive (ưu tiên gdown, fallback WebRequest)
function Get-DriveFile {
    param(
        [string]$FileId,
        [string]$Destination
    )
    try {
        # Bước 1: Thử tải bằng gdown (nếu có)
        $gdownOk = $false
        try {
            $null = & $pythonExe -c "import gdown; print('OK')" 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[*] Dùng gdown để tải file..." -ForegroundColor Cyan
                # gdown: cú pháp đúng: gdown <url> -O <output>
                $url = "https://drive.google.com/uc?id=$FileId"
                Write-Host "[DEBUG] gdown url: $url" -ForegroundColor Gray
                Write-Host "[DEBUG] gdown output: $Destination" -ForegroundColor Gray
                & $pythonExe -m gdown $url -O "$Destination" 2>&1
                Write-Host "[DEBUG] gdown exit code: $LASTEXITCODE" -ForegroundColor Gray
                if ($LASTEXITCODE -eq 0 -and (Test-Path $Destination)) {
                    $sz = (Get-Item $Destination).Length
                    Write-Host "[DEBUG] gdown file size: $sz bytes" -ForegroundColor Gray
                    if ($sz -gt 0) {
                        Write-Host "[+] Đã tải (gdown): $Destination"
                        $gdownOk = $true
                    } else {
                        Write-Host "[!] gdown tải file rỗng, thử cách khác..." -ForegroundColor Yellow
                    }
                } else {
                    Write-Host "[!] gdown thất bại (exit code $LASTEXITCODE), thử cách khác..." -ForegroundColor Yellow
                }
            }
        } catch {}

        if (-not $gdownOk) {
            # Bước 2: Fallback - WebRequest
            Write-Host "[*] Dùng WebRequest để tải file..." -ForegroundColor Cyan
            $session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
            $session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

            $downloadUrl = "https://drive.google.com/uc?export=download&id=$FileId"
            try {
                $resp = Invoke-WebRequest -Uri $downloadUrl -Method Get -WebSession $session -UseBasicParsing -TimeoutSec 30
                if ($resp.Content -match 'confirm=([^&"''>]+)') {
                    $confirmCode = $Matches[1]
                    $downloadUrl = "https://drive.google.com/uc?export=download&confirm=$confirmCode&id=$FileId"
                }
            } catch {}

            Invoke-WebRequest -Uri $downloadUrl -WebSession $session -OutFile $Destination -UseBasicParsing -TimeoutSec 600
        }

        # Bước 3: Kiểm tra kết quả chung
        if (-not (Test-Path $Destination)) {
            throw "File không tồn tại sau khi tải"
        }
        $fileSize = (Get-Item $Destination).Length
        if ($fileSize -eq 0) {
            # Kiểm tra nếu file là HTML
            $content = Get-Content $Destination -Raw -ErrorAction SilentlyContinue
            if ($content -match 'virus|scan|<html') {
                throw "Google Drive từ chối tải (virus scan). Link thủ công: https://drive.google.com/file/d/$FileId/view"
            }
            throw "File tải về bị rỗng (0 byte)"
        }

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
                Test-DownloadSize -FilePath $tlauncherExe -MinBytes 3145728 -Label "TLauncher"

                # 2. Tải GraalVM zip
                Write-Host "[2/3] Đang tải GraalVM..." -ForegroundColor Cyan
                Get-DriveFile -FileId $graalvmFileId -Destination $graalvmZip
                Test-DownloadSize -FilePath $graalvmZip -MinBytes 10485761 -Label "GraalVM"

                # 3. Tải versions.zip
                Write-Host "[3/3] Đang tải Versions..." -ForegroundColor Cyan
                Get-DriveFile -FileId $versionsFileId -Destination $versionsZip
                Test-DownloadSize -FilePath $versionsZip -MinBytes 10485761 -Label "Versions.zip"

                Write-Host "[✅] Đã tải đủ 3 file. Bắt đầu cài đặt..." -ForegroundColor Green

                # Gọi Work.py
                Invoke-PythonScriptInRam -ScriptPath $workPyUrl
                Write-Host "Nhánh 1 hoàn tất." -ForegroundColor Green
            } catch {
                Write-Host "Lỗi nhánh 1: $_" -ForegroundColor Red
            }
        }
        '2' {
            Write-Host "Bắt đầu nhánh 2: Upload phiên bản Minecraft..." -ForegroundColor Green
            try {
                # Tải secrets.enc về thư mục tạm
                $secretsEncPath = "$tempDir\secrets.enc"
                Write-Host "Đang tải secrets.enc..." -ForegroundColor Cyan
                $secretsUrl = "$REPO_RAW/secrets.enc"
                try {
                    $wc = New-Object System.Net.WebClient
                    $wc.Headers.Add("User-Agent", "Mozilla/5.0")
                    $wc.DownloadFile($secretsUrl, $secretsEncPath)
                } catch {
                    throw "Không thể tải secrets.enc từ repo: $_"
                }
                if (-not (Test-Path $secretsEncPath)) {
                    throw "File secrets.enc không tồn tại sau khi tải."
                }

                # Chạy decrypt_secrets.py với đường dẫn secrets.enc
                $output = Invoke-PythonScriptInRam -ScriptPath $decryptSecretsPyUrl -Arguments $secretsEncPath
                foreach ($line in $output) {
                    if ($line -match "^DISCORD_WEBHOOK_URL=(.+)$") {
                        $env:DISCORD_WEBHOOK_URL = $Matches[1]
                    }
                    if ($line -match "^GOOGLE_CREDENTIALS_PATH=(.+)$") {
                        $env:GOOGLE_CREDENTIALS_PATH = $Matches[1]
                    }
                }
                Write-Host "[✅] Secrets đã sẵn sàng." -ForegroundColor Green
                Invoke-PythonScriptInRam -ScriptPath $defendsPyUrl -Interactive
                Write-Host "[✅] Xác thực OTP thành công." -ForegroundColor Green
                Invoke-PythonScriptInRam -ScriptPath $uploadPyUrl
                Write-Host "[✅] Upload hoàn tất." -ForegroundColor Green
            } catch {
                Write-Host "Lỗi nhánh 2: $_" -ForegroundColor Red
            } finally {
                if ($env:GOOGLE_CREDENTIALS_PATH) {
                    Remove-Item $env:GOOGLE_CREDENTIALS_PATH -Force -ErrorAction SilentlyContinue
                }
                # Xóa secrets.enc tạm
                if (Test-Path "$tempDir\secrets.enc") {
                    Remove-Item "$tempDir\secrets.enc" -Force -ErrorAction SilentlyContinue
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

# Dọn dẹp thư mục tạm
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "[+] Đã dọn dẹp thư mục tạm." -ForegroundColor Gray
}

if ($host.Name -eq "ConsoleHost") {
    Write-Host "Nhấn Enter để thoát..." -ForegroundColor Yellow
    Read-Host
}
