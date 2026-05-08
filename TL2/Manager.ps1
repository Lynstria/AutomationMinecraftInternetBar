param($JsonPath)

$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$selected = @{}
$currentPos = 0

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
        Write-Host "$arrow$($i+1). $mark $($f.name) (Created: $($f.createdTime))"
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
                foreach ($n in $selected.Keys) {
                    Write-Host "Delete $n..." -ForegroundColor Red
                }
                $selected.Clear()
                Start-Sleep 1
            } else {
                $f = $files[$currentPos]
                Write-Host "Delete $($f.name)..." -ForegroundColor Red
                Start-Sleep 1
            }
        }
        elseif ($key -eq 81) { break }  # Q
    }
}

Main
