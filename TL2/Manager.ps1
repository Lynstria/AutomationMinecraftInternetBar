param($JsonPath)

$cache = @{}
$selected = @{}

function Write-Menu {
    param($files)
    Clear-Host
    Write-Host "=== Manager - Quản lý Versions ===" -ForegroundColor Green
    Write-Host "Space: Chọn/Bỏ chọn | 1: Đặt làm bản chính | 2: Xoá | Q: Quay lại" -ForegroundColor Yellow
    Write-Host ""
    for ($i = 0; $i -lt $files.Count; $i++) {
        $f = $files[$i]
        $mark = if ($selected[$f.name]) { "[X]" } else { "[ ]" }
        Write-Host "$($i+1). $mark $($f.name) (Created: $($f.createdTime))"
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
        Write-Menu $files
        $key = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown").VirtualKeyCode
        if ($key -eq 32) {  # Space
            # Toggle first unselected or selected (simplified)
            foreach ($f in $files) {
                if (-not $selected[$f.name]) {
                    $selected[$f.name] = $true
                    break
                }
            }
        }
        elseif ($key -eq 49) {  # 1
            if ($selected.Count -eq 1) {
                $name = ($selected.Keys)[0]
                Write-Host "Đặt $name làm bản chính (TL1 sẽ tải về)" -ForegroundColor Green
                # TODO: Update Drive file to mark as default
            } else {
                Write-Host "Chỉ chọn 1 phiên bản!" -ForegroundColor Red
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
            }
        }
        elseif ($key -eq 81) { break }  # Q
    }
}

Main
