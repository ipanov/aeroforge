# Simple FreeCAD Multi-Instance Launcher
# ========================================
#
# Launches 5 FreeCAD instances without attempting automatic configuration.
# User must manually configure MCP for each instance.
#
# Usage:
#   .\scripts\launch_freecad_simple.ps1

param(
    [int]$Count = 5,
    [string]$FreeCADPath = ""
)

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "FreeCAD Multi-Instance Launcher (Simple)" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

# Detect FreeCAD installation
if ($FreeCADPath -eq "") {
    $possiblePaths = @(
        "$env:LOCALAPPDATA\Programs\FreeCAD 1.0\bin\FreeCAD.exe",
        "C:\Users\$env:USERNAME\AppData\Local\Programs\FreeCAD 1.0\bin\FreeCAD.exe",
        "C:\Program Files\FreeCAD 1.0\bin\FreeCAD.exe",
        "C:\Program Files\FreeCAD 0.21\bin\FreeCAD.exe",
        "C:\Program Files\FreeCAD 0.20\bin\FreeCAD.exe",
        "$env:LOCALAPPDATA\Programs\FreeCAD\bin\FreeCAD.exe",
        "C:\FreeCAD\bin\FreeCAD.exe"
    )

    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            $FreeCADPath = $path
            break
        }
    }
}

if ($FreeCADPath -eq "" -or !(Test-Path $FreeCADPath)) {
    Write-Host "ERROR: FreeCAD executable not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please specify the path manually:" -ForegroundColor Yellow
    Write-Host '  .\scripts\launch_freecad_simple.ps1 -FreeCADPath "C:\Path\To\FreeCAD.exe"'
    Write-Host ""
    Write-Host "Or set environment variable:" -ForegroundColor Yellow
    Write-Host '  $env:FREECAD_PATH = "C:\Program Files\FreeCAD 1.0\bin\FreeCAD.exe"'
    Write-Host ""
    exit 1
}

Write-Host "FreeCAD Path: $FreeCADPath" -ForegroundColor Green
Write-Host "Launching: $Count instances" -ForegroundColor Green
Write-Host ""

# Launch instances
$processes = @()

for ($i = 1; $i -le $Count; $i++) {
    Write-Host "Launching Instance $i..." -ForegroundColor Cyan

    try {
        $process = Start-Process -FilePath $FreeCADPath -PassThru
        $processes += @{
            Instance = $i
            PID = $process.Id
        }

        Write-Host "  ✓ Launched (PID: $($process.Id))" -ForegroundColor Green

        # Delay between launches to avoid overwhelming system
        Start-Sleep -Milliseconds 1000

    } catch {
        Write-Host "  ✗ Failed: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "Manual Configuration Required" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

Write-Host "For EACH FreeCAD window ($Count total), complete these steps:" -ForegroundColor Yellow
Write-Host ""

Write-Host "Step 1: Select Workbench" -ForegroundColor White
Write-Host "  - Click the Workbench dropdown (top toolbar)" -ForegroundColor Gray
Write-Host "  - Select 'MCP Addon'" -ForegroundColor Gray
Write-Host ""

Write-Host "Step 2: Configure Port" -ForegroundColor White
Write-Host "  - Go to: Edit → Preferences → FreeCAD MCP" -ForegroundColor Gray
Write-Host "  - Set Port for each instance:" -ForegroundColor Gray

for ($i = 1; $i -le $Count; $i++) {
    $port = 9874 + $i
    Write-Host "     • Instance $i (PID $($processes[$i-1].PID)): Port $port" -ForegroundColor Cyan
}

Write-Host ""

Write-Host "Step 3: Start RPC Server" -ForegroundColor White
Write-Host "  - In the MCP toolbar, click 'Start RPC Server'" -ForegroundColor Gray
Write-Host "  - Server should start and show 'Running' status" -ForegroundColor Gray
Write-Host ""

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "Verification" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

Write-Host "After configuring all instances, verify they're working:" -ForegroundColor White
Write-Host ""
Write-Host "  python scripts/verify_freecad_instances.py" -ForegroundColor Cyan
Write-Host ""

Write-Host "Expected output:" -ForegroundColor White
Write-Host "  ✓ Port 9875: pong" -ForegroundColor Green
Write-Host "  ✓ Port 9876: pong" -ForegroundColor Green
Write-Host "  ✓ Port 9877: pong" -ForegroundColor Green
Write-Host "  ✓ Port 9878: pong" -ForegroundColor Green
Write-Host "  ✓ Port 9879: pong" -ForegroundColor Green
Write-Host "  Ready: 5/5 instances" -ForegroundColor Green
Write-Host ""

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

Write-Host "Press Enter to close this window (instances will remain running)..."
Read-Host
