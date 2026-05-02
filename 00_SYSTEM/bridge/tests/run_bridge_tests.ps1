$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

. "00_SYSTEM\bridge\governance\bridge_foundation_validator.ps1"

$result = Test-BridgeFoundation -RootPath "D:\CONTENT_ENGINE_OMEGA"

if ($result.status -ne "PASS") {
    Write-Host "[BRIDGE TEST FAIL]" -ForegroundColor Red
    Write-Host ($result | ConvertTo-Json -Depth 30)
    throw "BRIDGE FOUNDATION TEST FAILED: $($result.reason)"
}

Write-Host "[OK] BRIDGE FOUNDATION TEST PASS" -ForegroundColor Green