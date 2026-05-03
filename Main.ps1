#Requires -RunAsAdministrator
$ErrorActionPreference = "Stop"

# ======= CẤU HÌNH =======
$downloadPyUrl = "https://raw.githubusercontent.com/yourname/yourrepo/main/Download.py"
$workPyUrl     = "https://raw.githubusercontent.com/yourname/yourrepo/main/Work.py"
$defendsPyUrl  = "https://raw.githubusercontent.com/yourname/yourrepo/main/Defends.py"
$uploadPyUrl   = "https://raw.githubusercontent.com/yourname/yourrepo/main/Upload.py"

# Link Google Drive
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
pip install requests psutil gdown 2>$null

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
            $env:WORK_PY_B64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes((Invoke-WebRequest -Uri $workPyUrl -UseBasicParsing).Content))
            try {
                Invoke-PythonScriptInRam -ScriptUrl $downloadPyUrl -Arguments @("--graalvm-url", $graalvmZipDriveLink, "--versions-url", $versionsZipDriveLink)
                Write-Host "Nhánh 1 hoàn tất." -ForegroundColor Green
            } catch {
                Write-Host "Lỗi nhánh 1: $_" -ForegroundColor Red
            }
            finally {
                Remove-Item env:WORK_PY_B64 -ErrorAction SilentlyContinue
            }
        }
        '2' {
            Write-Host "Bắt đầu nhánh 2: Upload versions lên Drive..." -ForegroundColor Green
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