$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

. "00_SYSTEM\bridge\governance\bridge_v2_1_3_validator.ps1"

$result = Test-ManualBrainBridgeV213 -RootPath "D:\CONTENT_ENGINE_OMEGA"

if ($result.status -ne "PASS") {
    Write-Host "[BRIDGE V2.1.3 TEST FAIL]" -ForegroundColor Red
    Write-Host ($result | ConvertTo-Json -Depth 100)
    throw "BRIDGE V2.1.3 TEST FAILED: $($result.reason)"
}

Write-Host "[OK] BRIDGE V2.1.3 SOURCE RESOLVER + BRAIN READ-ONLY TEST PASS" -ForegroundColor Green