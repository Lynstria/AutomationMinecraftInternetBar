# Main.ps1 - Automation Minecraft Internet Bar
# Pipeline: PowerShell -> Python embed -> Download.py -> Exec.py -> CustomCore.py

$ErrorActionPreference = "Continue"

# GitHub raw base URL
$RAW_BASE = "https://raw.githubusercontent.com/Lynstria/AutomationMinecraftInternetBar/main/TL1"

function Write-LogPath {
    $desktop = [Environment]::GetFolderPath("Desktop")
    $dateStr = Get-Date -Format "HH-dd-MM"
    # PowerShell transcript log
    $logFile = Join-Path $desktop "mc-automation$dateStr.log"
    # Python logging log (separate to avoid file lock)
    $pythonLogFile = Join-Path $desktop "mc-automation${dateStr}_python.log"
    $logPathFile = Join-Path $env:TEMP "mc_log_path.txt"
    Set-Content -Path $logPathFile -Value $pythonLogFile -Encoding UTF8
    return $logFile
}

function Get-PythonEmbed {
    $embedUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
    $embedZip = Join-Path $env:TEMP "python_embed.zip"
    $embedDir = Join-Path $env:TEMP "python_embed"

    Write-Host "Downloading Python embed..." -ForegroundColor Cyan
    $headers = @{ "User-Agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" }
    Invoke-WebRequest -Uri $embedUrl -OutFile $embedZip -Headers $headers -TimeoutSec 120

    if (Test-Path $embedDir) {
        try { Remove-Item $embedDir -Recurse -Force -ErrorAction SilentlyContinue } catch {}
    }
    New-Item -ItemType Directory -Path $embedDir -Force | Out-Null

    Write-Host "Extracting Python embed..." -ForegroundColor Cyan
    Expand-Archive -Path $embedZip -DestinationPath $embedDir -Force

    # Download .py files
    $pyFiles = @("Download.py", "Exec.py", "CustomCore.py", "minecraft_tlauncher_java_config.json")
    foreach ($file in $pyFiles) {
        $url = "$RAW_BASE/$file"
        $dest = Join-Path $embedDir $file
        Write-Host "Downloading $file..." -ForegroundColor Cyan
        try {
            Invoke-WebRequest -Uri $url -OutFile $dest -Headers $headers -TimeoutSec 60
        } catch {
            Write-Host "Warning: Failed to download $file from GitHub: $_" -ForegroundColor Yellow
            # Try local copy
            $localFile = Join-Path $PSScriptRoot "TL1\$file"
            if (Test-Path $localFile) {
                Copy-Item $localFile $dest -Force
                Write-Host "Used local copy of $file" -ForegroundColor Green
            }
        }
    }

    return $embedDir
}

function Invoke-PythonScript {
    param($pythonDir, $scriptName)

    $pythonExe = Join-Path $pythonDir "python.exe"
    $scriptPath = Join-Path $pythonDir $scriptName

    if (-not (Test-Path $scriptPath)) {
        Write-Host "Script not found: $scriptPath" -ForegroundColor Red
        return $false
    }

    Write-Host "Running $scriptName..." -ForegroundColor Cyan
    $stdoutFile = Join-Path $env:TEMP "python_stdout.txt"
    $stderrFile = Join-Path $env:TEMP "python_stderr.txt"

    # Temporarily set ErrorActionPreference to Continue to avoid stop on Python errors
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

# Main
$logFile = Write-LogPath
Start-Transcript -Path $logFile -Append

Write-Host "=== Automation Minecraft Internet Bar ===" -ForegroundColor Green
Write-Host "1. Download (TL1)" -ForegroundColor Yellow
Write-Host "2. Upload (Coming soon)" -ForegroundColor Gray

$choice = Read-Host "Select option (1)"

$hasError = $false

if ($choice -eq "1") {
    Write-Host "Starting TL1 pipeline..." -ForegroundColor Green

    try {
        # Download Python embed + .py files
        $pythonDir = Get-PythonEmbed

        # Run Download.py
        $ok = Invoke-PythonScript -pythonDir $pythonDir -scriptName "Download.py"
        if (-not $ok) {
            Write-Host "Download.py FAILED!" -ForegroundColor Red
            $hasError = $true
        }

        # Run Exec.py (only if Download.py succeeded)
        if (-not $hasError) {
            $ok = Invoke-PythonScript -pythonDir $pythonDir -scriptName "Exec.py"
            if (-not $ok) {
                Write-Host "Exec.py FAILED!" -ForegroundColor Red
                $hasError = $true
            }
        }

        # Run CustomCore.py (only if Exec.py succeeded)
        if (-not $hasError) {
            $ok = Invoke-PythonScript -pythonDir $pythonDir -scriptName "CustomCore.py"
            if (-not $ok) {
                Write-Host "CustomCore.py FAILED!" -ForegroundColor Red
                $hasError = $true
            }
        }

        if (-not $hasError) {
            Write-Host "Nhánh 1 hoàn thành! Giờ bạn có thể mở Tlauncher và chơi Minecraft." -ForegroundColor Green
        }

    } catch {
        Write-Host "Pipeline error: $_" -ForegroundColor Red
        $hasError = $true
    }

    # Ask user about log
    Write-Host ""
    Write-Host "Log saved: $logFile" -ForegroundColor Cyan
    Write-Host "1. Giữ lại log" -ForegroundColor Yellow
    Write-Host "2. Xoá toàn bộ (temp files + log)" -ForegroundColor Yellow
    $cleanChoice = Read-Host "Select option"

    if ($cleanChoice -eq "2") {
        # Delete temp files
        $tempFiles = @(
            (Join-Path $env:TEMP "mc_path.txt"),
            (Join-Path $env:TEMP "mc_log_path.txt"),
            (Join-Path $env:TEMP "python_embed.zip"),
            (Join-Path $env:TEMP "python_embed"),
            (Join-Path $env:TEMP "GraalVM.zip"),
            (Join-Path $env:TEMP "versions.zip"),
            (Join-Path $env:TEMP "Tlauncher-Installer-1.9.5.1.exe")
        )
        foreach ($file in $tempFiles) {
            if (Test-Path $file) {
                Remove-Item $file -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
        # Delete log
        if (Test-Path $logFile) {
            Remove-Item $logFile -Force
            Write-Host "Deleted all temp files and log." -ForegroundColor Green
        }
    } else {
        Write-Host "Log kept: $logFile" -ForegroundColor Cyan
    }

} else {
    Write-Host "Upload feature coming soon." -ForegroundColor Yellow
}

Stop-Transcript
