& {
$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest
python 04_SCRIPTS\python\core\validate_phase_c.py
if(!(Test-Path "00_SYSTEM\core\classification\reports\PHASE_C_CLASSIFICATION_REPORT.md")){ throw "Missing classification report" }
if(!(Test-Path "00_SYSTEM\core\reports\PHASE_C_AUDIT_REPORT.md")){ throw "Missing audit report" }
Write-Host "PHASE C AUDIT: PASS"
}
