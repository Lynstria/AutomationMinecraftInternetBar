param($JsonPath)

$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$selected = @{}
$currentPos = 0
$DRIVE_FILE_ID = "1_JH04cXYbWSbhTmn3Y9jQFAf57DayWNM"

# Get access token from Code.txt (same dir as this script)
function Get-AccessToken {
    $codeFile = Join-Path $PSScriptRoot "Code.txt"
    if (-not (Test-Path $codeFile)) {
        Write-Host "Code.txt not found at $codeFile" -ForegroundColor Red
        return $null
    }
    $creds = Get-Content $codeFile | ConvertFrom-Json
    $body = "grant_type=refresh_token&refresh_token=$($creds.refresh_token)&client_id=$($creds.client_id)&client_secret=$($creds.client_secret)"
    try {
        $resp = Invoke-RestMethod -Uri "https://oauth2.googleapis.com/token" -Method POST -Body $body -ContentType "application/x-www-form-urlencoded"
        return $resp.access_token
    } catch {
        Write-Host "Failed to get access token: $($_)" -ForegroundColor Red
        return $null
    }
}

# Delete revisions via Drive API
function Remove-Revisions {
    param($revIds)
    $token = Get-AccessToken
    if (-not $token) { return $false }
    $ok = $true
    foreach ($id in $revIds) {
        $url = "https://www.googleapis.com/drive/v3/files/$DRIVE_FILE_ID/revisions/$id"
        try {
            Invoke-RestMethod -Uri $url -Method DELETE -Headers @{ Authorization = "Bearer $token" } | Out-Null
            Write-Host "Deleted revision $id" -ForegroundColor Green
        } catch {
            Write-Host "Failed to delete ${id}: $($_)" -ForegroundColor Red
            $ok = $false
        }
    }
    return $ok
}

function Write-Menu {
    param($files, $pos)
    Clear-Host
    Write-Host "=== Manager - Manage Versions ===" -ForegroundColor Green
    Write-Host "Up/Down: Move | Space: Toggle select | 1: Set as main | 2: Delete | Q: Back" -ForegroundColor Yellow
    Write-Host ""
    for ($i = 0; $i -lt $files.Count; $i++) {
        $f = $files[$i]
        $mark = if ($selected[$f.name]) { "[X]" } else { "[ ]" }
        $arrow = if ($i -eq $pos) { ">" } else { " " }
        $size = if ($f.size) { " ($($f.size))" } else { "" }
        Write-Host "$arrow$($i+1). $mark $($f.name)$size (Created: $($f.createdTime))"
    }
}

function Main {
    if (-not (Test-Path $JsonPath)) {
        Write-Host "Not found: $JsonPath" -ForegroundColor Red
        exit 1
    }
    $files = Get-Content $JsonPath | ConvertFrom-Json
    if ($files.Count -eq 0) {
        Write-Host "No files in Drive folder." -ForegroundColor Yellow
        Start-Sleep 2
        exit 0
    }
    $files = @($files)

    while ($true) {
        Write-Menu $files $currentPos
        $key = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown").VirtualKeyCode
        if ($key -eq 38) {  # Up
            if ($currentPos -gt 0) { $currentPos-- }
        }
        elseif ($key -eq 40) {  # Down
            if ($currentPos -lt $files.Count - 1) { $currentPos++ }
        }
        elseif ($key -eq 32) {  # Space toggle
            $f = $files[$currentPos]
            $selected[$f.name] = -not $selected[$f.name]
        }
        elseif ($key -eq 49) {  # 1
            if ($selected.Count -eq 1) {
                $name = ($selected.Keys)[0]
                Write-Host "Set '$name' as main version (TL1 will download)" -ForegroundColor Green
                Start-Sleep 1
            } elseif ($selected.Count -gt 1) {
                Write-Host "Select only 1 version!" -ForegroundColor Red
                Start-Sleep 1
            } else {
                $f = $files[$currentPos]
                $selected[$f.name] = $true
                Write-Host "Selected '$($f.name)' as main" -ForegroundColor Green
                Start-Sleep 1
            }
        }
        elseif ($key -eq 50) {  # 2
            if ($selected.Count -gt 0) {
                $revIds = @()
                foreach ($k in $selected.Keys) {
                    # Extract revision ID from name like "versions.zip (rev abc123)"
                    if ($k -match '\(rev ([^)]+)\)') {
                        $revIds += $matches[1]
                    }
                }
                if ($revIds.Count -gt 0) {
                    Write-Host "Deleting $($revIds.Count) revision(s)..." -ForegroundColor Red
                    $ok = Remove-Revisions $revIds
                    if ($ok) {
                        # Remove deleted entries from $files
                        $files = $files | Where-Object { $revIds -notcontains ($_.id) }
                        $files = @($files)
                        $selected.Clear()
                        Write-Host "Deleted. Refreshing list..." -ForegroundColor Green
                        Start-Sleep 1
                    }
                }
            } else {
                $f = $files[$currentPos]
                Write-Host "Delete $($f.name)..." -ForegroundColor Red
                if ($f.id -match '^[^)]+$') {
                    $ok = Remove-Revisions @($f.id)
                }
                Start-Sleep 1
            }
        }
        elseif ($key -eq 81) { break }  # Q
    }
}

Main
