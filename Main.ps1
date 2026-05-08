# Main.ps1 - Automation Minecraft Internet Bar
# Pipeline: Download repo.zip -> python_embed -> TL1/TL2

$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"
$env:PYTHONUNBUFFERED = "1"

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
    param($pythonDir, $scriptName, $scriptPath)

    $pythonExe = Join-Path $pythonDir "python.exe"
    if (-not $scriptPath) {
        $scriptPath = Join-Path $pythonDir $scriptName
    }

    if (-not (Test-Path $scriptPath)) {
        Write-Host "Script not found: $scriptPath" -ForegroundColor Red
        return $false
    }

    $prevErrorPref = $ErrorActionPreference
    $ErrorActionPreference = "Continue"

    & $pythonExe $scriptPath
    $exitCode = $LASTEXITCODE

    $ErrorActionPreference = $prevErrorPref

    if ($exitCode -ne 0) {
        Write-Host "$scriptName exited with code $exitCode" -ForegroundColor Red
        return $false
    }
    return $true
}

# Check if repo already exists with essential files
$essentialFiles = @(
    (Join-Path $repoDir "Main.ps1"),
    (Join-Path $repoDir "TL1\Download.py"),
    (Join-Path $repoDir "TL1\Exec.py"),
    (Join-Path $repoDir "TL1\CustomCore.py"),
    (Join-Path $repoDir "TL2\nothing.enc"),
    (Join-Path $repoDir "TL2\Decode.py"),
    (Join-Path $repoDir "TL2\Shield.py"),
    (Join-Path $repoDir "TL2\Menu2.py")
)

$repoReady = $false
if (Test-Path $repoDir) {
    $allExist = $true
    foreach ($f in $essentialFiles) {
        if (-not (Test-Path $f)) {
            $allExist = $false
            break
        }
    }
    if ($allExist) {
        Write-Host "Repo already exists with all files, skipping download." -ForegroundColor Green
        $repoReady = $true
    } else {
        Write-Host "Repo exists but missing files, re-downloading..." -ForegroundColor Yellow
    }
}

if (-not $repoReady) {
    try {
        Get-WebFile -url $repoUrl -outFile $repoZip -activity "Downloading repo"
        if (Test-Path $repoDir) {
            Remove-Item $repoDir -Recurse -Force -ErrorAction SilentlyContinue
        }
        Expand-Archive -Path $repoZip -DestinationPath $env:TEMP -Force
        Write-Host "Repo extracted" -ForegroundColor Green

        # Verify essential files after extract
        $missing = $false
        foreach ($f in $essentialFiles) {
            if (-not (Test-Path $f)) {
                Write-Host "Missing file: $f" -ForegroundColor Red
                $missing = $true
            }
        }
        if ($missing) {
            Write-Host "Repo missing files. Check GitHub repo." -ForegroundColor Red
            exit 1
        }
        Write-Host "All files ok" -ForegroundColor Green
        $repoReady = $true
    } catch {
        Write-Host "Failed to download repo: $_" -ForegroundColor Red
        exit 1
    }
}

# Download Python embed (skip if exists)
$embedUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
$embedZip = Join-Path $env:TEMP "python_embed.zip"
$embedDir = Join-Path $repoDir "python_embed"

$embedReady = $false
if ((Test-Path $embedDir) -and (Test-Path (Join-Path $embedDir "python.exe"))) {
    Write-Host "Python embed already exists, skipping download." -ForegroundColor Green
    $embedReady = $true
}

if (-not $embedReady) {
    try {
        Get-WebFile -url $embedUrl -outFile $embedZip -activity "Downloading Python embed"
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
}

while ($true) {
    Write-Host "=== Automation Minecraft Internet Bar ===" -ForegroundColor Green
    Write-Host "1. Download (TL1)" -ForegroundColor Yellow
    Write-Host "2. Upload (TL2)" -ForegroundColor Yellow
    Write-Host "3. Exit" -ForegroundColor Yellow

    $choice = Read-Host "Select option (1-3)"

    $hasError = $false

    if ($choice -eq "1") {
        try {
            $tl1Dir = Join-Path $repoDir "TL1"
            $ok = Invoke-PythonScript -pythonDir $embedDir -scriptPath (Join-Path $tl1Dir "Download.py")
            if (-not $ok) {
                Write-Host "Download.py FAILED!" -ForegroundColor Red
                $hasError = $true
            }

            if (-not $hasError) {
                $ok = Invoke-PythonScript -pythonDir $embedDir -scriptPath (Join-Path $tl1Dir "Exec.py")
                if (-not $ok) {
                    Write-Host "Exec.py FAILED!" -ForegroundColor Red
                    $hasError = $true
                }
            }

            if (-not $hasError) {
                $ok = Invoke-PythonScript -pythonDir $embedDir -scriptPath (Join-Path $tl1Dir "CustomCore.py")
                if (-not $ok) {
                    Write-Host "CustomCore.py FAILED!" -ForegroundColor Red
                    $hasError = $true
                }
            }

            if (-not $hasError) {
                Write-Host "Branch 1 done! You can open Tlauncher and play Minecraft." -ForegroundColor Green
            }

        } catch {
            Write-Host "Pipeline error: $_" -ForegroundColor Red
            $hasError = $true
        }

        # Ask user about temp files
        Write-Host ""
        Write-Host "1. Keep temp files (repo + python_embed)" -ForegroundColor Yellow
        Write-Host "2. Delete all (temp files + repo)" -ForegroundColor Yellow
        $cleanChoice = Read-Host "Select option"

        if ($cleanChoice -eq "2") {
            $tempFiles = @(
                (Join-Path $env:TEMP "mc_path.txt"),
                (Join-Path $env:TEMP "python_embed.zip"),
                (Join-Path $env:TEMP "python_embed"),
                (Join-Path $env:TEMP "GraalVM.zip"),
                (Join-Path $env:TEMP "versions.zip"),
                (Join-Path $env:TEMP "Tlauncher-Installer-1.9.5.1.exe"),
                $repoDir
            )
            foreach ($file in $tempFiles) {
                if (Test-Path $file) {
                    Remove-Item $file -Recurse -Force -ErrorAction SilentlyContinue
                }
            }
            Write-Host "Deleted all temp files and repo." -ForegroundColor Green
        } else {
            Write-Host "Temp files kept: $repoDir, $embedDir" -ForegroundColor Cyan
        }

    } elseif ($choice -eq "2") {
        Write-Host "Starting TL2 pipeline..." -ForegroundColor Green
        $pythonExe = Join-Path $embedDir "python.exe"
        $repoRoot = $repoDir

        $nothingEnc = Join-Path $repoRoot "TL2\nothing.enc"
        if (-not (Test-Path $nothingEnc)) {
            Write-Host "Error: nothing.enc not found at $nothingEnc" -ForegroundColor Red
            continue
        }

        $decodePs1 = Join-Path $repoRoot "TL2\Decode.py"
        Write-Host "Decrypting..." -ForegroundColor Cyan
        & $pythonExe $decodePs1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Decryption failed!" -ForegroundColor Red
        } else {
            Write-Host "Decryption successful!" -ForegroundColor Green

            $shieldPs1 = Join-Path $repoRoot "TL2\Shield.py"
            Write-Host "Sending auth code..." -ForegroundColor Cyan
            & $pythonExe $shieldPs1
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Auth send failed!" -ForegroundColor Red
            } else {
                Write-Host "Auth sent!" -ForegroundColor Green

                $menu2Ps1 = Join-Path $repoRoot "TL2\Menu2.py"
                Write-Host "Opening Menu2..." -ForegroundColor Cyan
                & $pythonExe $menu2Ps1
                if ($LASTEXITCODE -ne 0) {
                    Write-Host "Menu2 failed!" -ForegroundColor Red
                } else {
                    Write-Host "Menu2 opened!" -ForegroundColor Green
                }
            }
        }

    } elseif ($choice -eq "3") {
        break
    }
}
