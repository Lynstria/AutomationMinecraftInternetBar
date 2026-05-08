# Main.ps1 - Automation Minecraft Internet Bar
# Pipeline: Download repo.zip -> python_embed -> TL1/TL2

$ErrorActionPreference = "Continue"

# GitHub raw base URL
$RAW_BASE = "https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/TL1"

# Download repo.zip + python_embed.zip first
$repoUrl = "https://github.com/Lynstria/AutomationMinecraftInternetBar/archive/refs/heads/main.zip"
$repoZip = Join-Path $env:TEMP "repo_main.zip"
$repoDir = Join-Path $env:TEMP "AutomationMinecraftInternetBar-main"

$headers = @{ "User-Agent" = "Mozilla/5.0" }

# Helper: Download file with progress
function Get-WebFile {
    param($url, $outFile, $activity)
    Write-Host "$activity..." -NoNewline
    try {
        Invoke-WebRequest -Uri $url -OutFile $outFile -Headers $global:headers -TimeoutSec 300
        Write-Host " 100%" -NoNewline
    } catch {
        Write-Host " FAILED" -NoNewline
        throw
    } finally {
        Write-Host ""
    }
}

function Invoke-PythonScript {
    param($pythonDir, $scriptName)

    $pythonExe = Join-Path $pythonDir "python.exe"
    $scriptPath = Join-Path $pythonDir $scriptName

    if (-not (Test-Path $scriptPath)) {
        Write-Host "Script not found: $scriptPath" -ForegroundColor Red
        return $false
    }

    $stdoutFile = Join-Path $env:TEMP "python_stdout.txt"
    $stderrFile = Join-Path $env:TEMP "python_stderr.txt"

    $prevErrorPref = $ErrorActionPreference
    $ErrorActionPreference = "Continue"

    & $pythonExe $scriptPath > $stdoutFile 2> $stderrFile
    $exitCode = $LASTEXITCODE

    $ErrorActionPreference = $prevErrorPref

    if (Test-Path $stdoutFile) {
        $stdout = Get-Content $stdoutFile -Raw
        if ($stdout) { Write-Host $stdout }
        Remove-Item $stdoutFile -Force -ErrorAction SilentlyContinue
    }
    if (Test-Path $stderrFile) {
        $stderr = Get-Content $stderrFile -Raw
        if ($stderr) { Write-Host "STDERR: $stderr" -ForegroundColor Yellow }
        Remove-Item $stderrFile -Force -ErrorAction SilentlyContinue
    }

    if ($exitCode -ne 0) {
        Write-Host "$scriptName exited with code $exitCode" -ForegroundColor Red
        return $false
    }
    return $true
}

try {
    Get-WebFile -url $repoUrl -outFile $repoZip -activity "Dang tai repo"
    if (Test-Path $repoDir) {
        Remove-Item $repoDir -Recurse -Force -ErrorAction SilentlyContinue
    }
    Expand-Archive -Path $repoZip -DestinationPath $env:TEMP -Force
    Write-Host "Repo extracted" -ForegroundColor Green

    # Check required TL2 files (especially nothing.enc)
    $tl2Files = @(
        (Join-Path $repoDir "TL2\nothing.enc"),
        (Join-Path $repoDir "TL2\Decode.py"),
        (Join-Path $repoDir "TL2\Shield.py"),
        (Join-Path $repoDir "TL2\Menu2.py"),
        (Join-Path $repoDir "TL2\lib_pure\aes_pure.py")
    )
    $missing = $false
    foreach ($file in $tl2Files) {
        if (-not (Test-Path $file)) {
            Write-Host "Thieu file: $file" -ForegroundColor Red
            $missing = $true
        }
    }
    if ($missing) {
        Write-Host "Repo khong day du file. Hay kiem tra GitHub repo." -ForegroundColor Red
        exit 1
    }
    Write-Host "Tat ca file TL2 ok" -ForegroundColor Green
} catch {
    Write-Host "Failed to download repo: $_" -ForegroundColor Red
    exit 1
}

# Download Python embed
$embedUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
$embedZip = Join-Path $env:TEMP "python_embed.zip"
$embedDir = Join-Path $repoDir "python_embed"

try {
    Get-WebFile -url $embedUrl -outFile $embedZip -activity "Dang tai Python embed"
    if (Test-Path $embedDir) {
        Remove-Item $embedDir -Recurse -Force -ErrorAction SilentlyContinue
    }
    New-Item -ItemType Directory -Path $embedDir -Force | Out-Null
    Expand-Archive -Path $embedZip -DestinationPath $embedDir -Force
    Write-Host "Python embed ready" -ForegroundColor Green
} catch {
    Write-Host "Failed to download Python embed: $_" -ForegroundColor Red
    exit 1
}

# Log setup
function Write-LogPath {
    $desktop = [Environment]::GetFolderPath("Desktop")
    $dateStr = Get-Date -Format "HH-dd-MM"
    $logFile = Join-Path $desktop "mc-automation$dateStr.log"
    $pythonLogFile = Join-Path $desktop "mc-automation${dateStr}_python.log"
    $logPathFile = Join-Path $env:TEMP "mc_log_path.txt"
    Set-Content -Path $logPathFile -Value $pythonLogFile -Encoding UTF8
    return $logFile
}

$logFile = Write-LogPath
Start-Transcript -Path $logFile -Append

Write-Host "=== Automation Minecraft Internet Bar ===" -ForegroundColor Green
Write-Host "1. Download (TL1)" -ForegroundColor Yellow
Write-Host "2. Upload (TL2)" -ForegroundColor Yellow

$choice = Read-Host "Select option (1)"

$hasError = $false

if ($choice -eq "1") {
    Write-Host "Starting TL1 pipeline..." -ForegroundColor Green

    try {
        # Download .py files to python_embed dir
        $pyFiles = @("Download.py", "Exec.py", "CustomCore.py", "minecraft_tlauncher_java_config.json")
        Write-Host "Dang tai cac file TL1..." -ForegroundColor Cyan
        $total = $pyFiles.Count
        $count = 0
        foreach ($file in $pyFiles) {
            $count++
            $percent = [math]::Floor(($count / $total) * 100)
            Show-Progress $percent "TL1 files"
            $url = "$RAW_BASE/$file"
            $dest = Join-Path $embedDir $file
            try {
                Invoke-WebRequest -Uri $url -OutFile $dest -Headers $headers -TimeoutSec 60
            } catch {
                Write-Host "`nWarning: Failed to download $file from GitHub: $_" -ForegroundColor Yellow
                $localFile = Join-Path $PSScriptRoot "TL1\$file"
                if (Test-Path $localFile) {
                    Copy-Item $localFile $dest -Force
                    Write-Host "Used local copy of $file" -ForegroundColor Green
                }
            }
        }
        Show-Progress 100 "TL1 files"
        Write-Host ""

        # Run Download.py
        $ok = Invoke-PythonScript -pythonDir $embedDir -scriptName "Download.py"
        if (-not $ok) {
            Write-Host "Download.py FAILED!" -ForegroundColor Red
            $hasError = $true
        }

        # Run Exec.py (only if Download.py succeeded)
        if (-not $hasError) {
            $ok = Invoke-PythonScript -pythonDir $embedDir -scriptName "Exec.py"
            if (-not $ok) {
                Write-Host "Exec.py FAILED!" -ForegroundColor Red
                $hasError = $true
            }
        }

        # Run CustomCore.py (only if Exec.py succeeded)
        if (-not $hasError) {
            $ok = Invoke-PythonScript -pythonDir $embedDir -scriptName "CustomCore.py"
            if (-not $ok) {
                Write-Host "CustomCore.py FAILED!" -ForegroundColor Red
                $hasError = $true
            }
        }

        if (-not $hasError) {
            Write-Host "Nhanh 1 hoan thanh! Gio ban co the mo Tlauncher va choi Minecraft." -ForegroundColor Green
        }

    } catch {
        Write-Host "Pipeline error: $_" -ForegroundColor Red
        $hasError = $true
    }

    # Ask user about log
    Write-Host ""
    Write-Host "Log saved: $logFile" -ForegroundColor Cyan
    Write-Host "1. Giu lai log" -ForegroundColor Yellow
    Write-Host "2. Xoa toan bo (temp files + log)" -ForegroundColor Yellow
    $cleanChoice = Read-Host "Select option"

    if ($cleanChoice -eq "2") {
        $tempFiles = @(
            (Join-Path $env:TEMP "mc_path.txt"),
            (Join-Path $env:TEMP "mc_log_path.txt"),
            (Join-Path $env:TEMP "python_embed.zip"),
            (Join-Path $env:TEMP "python_embed"),
            (Join-Path $env:TEMP "GralVM.zip"),
            (Join-Path $env:TEMP "versions.zip"),
            (Join-Path $env:TEMP "Tlauncher-Installer-1.9.5.1.exe")
        )
        foreach ($file in $tempFiles) {
            if (Test-Path $file) {
                Remove-Item $file -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
        if (Test-Path $logFile) {
            Remove-Item $logFile -Force
            Write-Host "Deleted all temp files and log." -ForegroundColor Green
        }
    } else {
        Write-Host "Log kept: $logFile" -ForegroundColor Cyan
    }

} else {
    Write-Host "Starting TL2 pipeline..." -ForegroundColor Green
    $pythonExe = Join-Path $embedDir "python.exe"
    $repoRoot = $repoDir

    # Check nothing.enc exists before running Decode.py
    $nothingEnc = Join-Path $repoRoot "TL2\nothing.enc"
    if (-not (Test-Path $nothingEnc)) {
        Write-Host "Loi: Khong tim thay nothing.enc tai $nothingEnc" -ForegroundColor Red
        exit 1
    }

    # Run Decode.py
    $decodePs1 = Join-Path $repoRoot "TL2\Decode.py"
    Write-Host "Dang giai ma..." -ForegroundColor Cyan
    & $pythonExe $decodePs1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Giai ma that bai!" -ForegroundColor Red
    } else {
        Write-Host "Giai ma thanh cong!" -ForegroundColor Green

        # Run Shield.py
        $shieldPs1 = Join-Path $repoRoot "TL2\Shield.py"
        Write-Host "Dang gui ma xac thuc..." -ForegroundColor Cyan
        & $pythonExe $shieldPs1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Gui ma that bai!" -ForegroundColor Red
        } else {
            Write-Host "Da gui ma xac thuc!" -ForegroundColor Green

            # Run Menu2.py
            $menu2Ps1 = Join-Path $repoRoot "TL2\Menu2.py"
            Write-Host "Dang mo Menu2..." -ForegroundColor Cyan
            & $pythonExe $menu2Ps1
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Menu2 that bai!" -ForegroundColor Red
            } else {
                Write-Host "Menu2 da mo!" -ForegroundColor Green
            }
        }
    }
}

Stop-Transcript

