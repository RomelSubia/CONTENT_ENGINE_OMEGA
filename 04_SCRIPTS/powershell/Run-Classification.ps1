& {
$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest
$Root="D:\CONTENT_ENGINE_OMEGA"
Set-Location $Root
if((Get-Location).Path -ne $Root){ throw "BLOCKED: wrong root" }
if($Root -like "*ARGOS*"){ throw "BLOCKED: ARGOS scope" }
if(Test-Path ".\.venv\Scripts\Activate.ps1"){ . ".\.venv\Scripts\Activate.ps1" }

python 04_SCRIPTS\python\core\validate_phase0.py
python 04_SCRIPTS\python\core\validate_phase_a.py
python 04_SCRIPTS\python\core\validate_phase_b.py

$Lock="00_SYSTEM\core\classification\locks\classification.lock"
if(Test-Path $Lock){ throw "BLOCKED: classification.lock active" }

'{"phase":"C","status":"running"}' | Set-Content $Lock -Encoding UTF8
try {
    python 04_SCRIPTS\python\core\classification_engine.py
}
finally {
    if(Test-Path $Lock){ Remove-Item $Lock -Force }
}
Write-Host "PHASE_C_RUN: PASS"
}
