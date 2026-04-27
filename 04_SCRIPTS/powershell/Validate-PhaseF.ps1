& {
$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest
python 04_SCRIPTS\python\core\validate_phase_f.py
if($LASTEXITCODE -ne 0){ throw "BLOCKED: validate_phase_f failed" }
if(!(Test-Path "00_SYSTEM\core\loop\reports\PHASE_F_LOOP_REPORT.md")){ throw "Missing loop report" }
if(!(Test-Path "00_SYSTEM\core\reports\PHASE_F_AUDIT_REPORT.md")){ throw "Missing audit report" }
Write-Host "PHASE F AUDIT: PASS"
}
