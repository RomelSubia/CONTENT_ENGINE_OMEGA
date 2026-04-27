& {
$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

python 04_SCRIPTS\python\core\validate_phase_c5.py
if($LASTEXITCODE -ne 0){ throw "BLOCKED: validate_phase_c5.py failed" }

if(!(Test-Path "00_SYSTEM\core\dev_self_governance\reports\PHASE_C5_DEV_GOVERNANCE_REPORT.md")){
    throw "BLOCKED: missing C5 dev report"
}
if(!(Test-Path "00_SYSTEM\core\reports\PHASE_C5_AUDIT_REPORT.md")){
    throw "BLOCKED: missing C5 audit report"
}

Write-Host "PHASE C5 AUDIT: PASS"
}
