& {
$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

$Root="D:\CONTENT_ENGINE_OMEGA"
Set-Location $Root

if((Get-Location).Path -ne $Root){ throw "BLOCKED: wrong root" }
if($Root -like "*ARGOS*"){ throw "BLOCKED: ARGOS scope" }
if(Test-Path ".\.venv\Scripts\Activate.ps1"){ . ".\.venv\Scripts\Activate.ps1" }

python 04_SCRIPTS\python\core\dev_self_governance.py
Write-Host "PHASE_C5_RUN: PASS"
}