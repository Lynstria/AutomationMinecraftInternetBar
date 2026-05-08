param($JsonPath)

$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$selected = @{}
$currentPos = 0

function Write-Menu {
    param($files, $pos)
    Clear-Host
    Write-Host "=== Manager - Quản lý Versions ===" -ForegroundColor Green
    Write-Host "↑↓: Di chuyển | Space: Chọn/Bỏ chọn | 1: Đặt làm bản chính | 2: Xoá | Q: Quay lại" -ForegroundColor Yellow
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
        Write-Host "Không tìm thấy $JsonPath" -ForegroundColor Red
        exit 1
    }
    $files = Get-Content $JsonPath | ConvertFrom-Json
    if ($files.Count -eq 0) {
        Write-Host "Không có file nào trong Drive folder." -ForegroundColor Yellow
        Start-Sleep 2
        exit 0
    }
    $files = @($files)  # Ensure array

    while ($true) {
        Write-Menu $files $currentPos
        $key = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown").VirtualKeyCode
        if ($key -eq 38) {  # Up arrow
            if ($currentPos -gt 0) { $currentPos-- }
        }
        elseif ($key -eq 40) {  # Down arrow
            if ($currentPos -lt $files.Count - 1) { $currentPos++ }
        }
        elseif ($key -eq 32) {  # Space - toggle
            $f = $files[$currentPos]
            $selected[$f.name] = -not $selected[$f.name]
        }
        elseif ($key -eq 49) {  # 1
            if ($selected.Count -eq 1) {
                $name = ($selected.Keys)[0]
                Write-Host "Đặt '$name' làm bản chính (TL1 sẽ tải về)" -ForegroundColor Green
                Start-Sleep 1
                # TODO: Update Drive file to mark as default
            } elseif ($selected.Count -gt 1) {
                Write-Host "Chỉ chọn 1 phiên bản!" -ForegroundColor Red
                Start-Sleep 1
            } else {
                # Không có gì chọn, dùng currentPos
                $f = $files[$currentPos]
                $selected[$f.name] = $true
                Write-Host "Đã chọn '$($f.name)' để đặt làm bản chính" -ForegroundColor Green
                Start-Sleep 1
            }
        }
        elseif ($key -eq 50) {  # 2
            if ($selected.Count -gt 0) {
                foreach ($n in $selected.Keys) {
                    Write-Host "Xoá $n..." -ForegroundColor Red
                    # TODO: Delete from Drive API
                }
                $selected.Clear()
                Start-Sleep 1
            } else {
                # Không chọn gì, xoá item tại currentPos
                $f = $files[$currentPos]
                Write-Host "Xoá $($f.name)..." -ForegroundColor Red
                Start-Sleep 1
            }
        }
        elseif ($key -eq 81) { break }  # Q
    }
}

Main
