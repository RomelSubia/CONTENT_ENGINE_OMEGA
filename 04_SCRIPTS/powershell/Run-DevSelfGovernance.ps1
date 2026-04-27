& {
$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

$Root="D:\CONTENT_ENGINE_OMEGA"
Set-Location $Root

if((Get-Location).Path -ne $Root){ throw "BLOCKED: wrong root" }
if($Root -like "*ARGOS*"){ throw "BLOCKED: ARGOS scope" }
if(Test-Path ".\.venv\Scripts\Activate.ps1"){ . ".\.venv\Scripts\Activate.ps1" }

python 04_SCRIPTS\python\core\dev_self_governance.py
if($LASTEXITCODE -ne 0){ throw "BLOCKED: dev_self_governance.py failed" }

if(!(Test-Path "00_SYSTEM\core\dev_self_governance\reports\PHASE_C5_DEV_GOVERNANCE_REPORT.md")){
    throw "BLOCKED: missing C5 dev report"
}
if(!(Test-Path "00_SYSTEM\core\reports\PHASE_C5_AUDIT_REPORT.md")){
    throw "BLOCKED: missing C5 audit report"
}

Write-Host "PHASE_C5_RUN: PASS"
}
