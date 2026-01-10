# Script to kill Pyre language server processes
# This forces a reload of the .pyre_configuration

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 59 -ForegroundColor Cyan
Write-Host "Killing Pyre Language Server Processes" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 59 -ForegroundColor Cyan
Write-Host ""

# Kill pyrefly.exe
$pyrefly = Get-Process -Name "pyrefly" -ErrorAction SilentlyContinue
if ($pyrefly) {
    Write-Host "[1/2] Killing pyrefly.exe..." -ForegroundColor Yellow
    Stop-Process -Name "pyrefly" -Force
    Write-Host "      ✓ pyrefly.exe killed" -ForegroundColor Green
} else {
    Write-Host "[1/2] pyrefly.exe not running" -ForegroundColor Gray
}

# Kill language_server_windows_x64.exe
$langserver = Get-Process -Name "language_server_windows_x64" -ErrorAction SilentlyContinue
if ($langserver) {
    Write-Host "[2/2] Killing language_server_windows_x64.exe..." -ForegroundColor Yellow
    Stop-Process -Name "language_server_windows_x64" -Force
    Write-Host "      ✓ language_server_windows_x64.exe killed" -ForegroundColor Green
} else {
    Write-Host "[2/2] language_server_windows_x64.exe not running" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 59 -ForegroundColor Cyan
Write-Host "Done! Please reload your IDE window now." -ForegroundColor Green
Write-Host "In VS Code: Ctrl+Shift+P → 'Developer: Reload Window'" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 59 -ForegroundColor Cyan
