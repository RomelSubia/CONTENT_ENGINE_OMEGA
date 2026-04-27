& {
$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest
$Root="D:\CONTENT_ENGINE_OMEGA"
Set-Location $Root
if((Get-Location).Path -ne $Root){ throw "BLOCKED: wrong root" }
if($Root -like "*ARGOS*"){ throw "BLOCKED: ARGOS scope" }
python 04_SCRIPTS\python\core\loop_core.py
if($LASTEXITCODE -ne 0){ throw "BLOCKED: loop_core failed" }
Write-Host "PHASE_F_RUN: PASS"
}
