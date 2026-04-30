function Get-StableHash {
    param([Parameter(Mandatory=$true)][string]$Text)

    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $hash = $sha.ComputeHash($bytes)
    return ([BitConverter]::ToString($hash)).Replace("-", "").ToLowerInvariant()
}

function Write-AtomicEvidence {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [Parameter(Mandatory=$true)][string]$Content
    )

    $Dir = Split-Path $Path
    if (!(Test-Path $Dir)) {
        New-Item -ItemType Directory -Force -Path $Dir | Out-Null
    }

    $Tmp = "$Path.tmp"

    $Content | Set-Content $Tmp -Encoding UTF8

    if (!(Test-Path $Tmp)) {
        return @{
            status = "BLOCK"
            reason = "TMP_WRITE_FAILED"
        }
    }

    $ExpectedHash = Get-StableHash -Text $Content
    $TmpContent = Get-Content $Tmp -Raw
    $TmpHash = Get-StableHash -Text $TmpContent

    if ($TmpHash -ne $ExpectedHash) {
        Remove-Item $Tmp -Force -ErrorAction SilentlyContinue
        return @{
            status = "LOCK"
            reason = "TMP_HASH_MISMATCH"
        }
    }

    Move-Item $Tmp $Path -Force

    if (!(Test-Path $Path)) {
        return @{
            status = "BLOCK"
            reason = "ATOMIC_PUBLISH_FAILED"
        }
    }

    $FinalContent = Get-Content $Path -Raw
    $FinalHash = Get-StableHash -Text $FinalContent

    if ($FinalHash -ne $ExpectedHash) {
        return @{
            status = "LOCK"
            reason = "FINAL_HASH_MISMATCH"
        }
    }

    return @{
        status = "TRACE_RECORDED"
        evidence_hash = $FinalHash
        path = $Path
    }
}
