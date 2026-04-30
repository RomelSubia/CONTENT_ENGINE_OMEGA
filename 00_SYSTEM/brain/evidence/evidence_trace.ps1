function Get-StableHash {
    param([Parameter(Mandatory=$true)][string]$Text)

    $bytes = [System.Text.UTF8Encoding]::new($false).GetBytes($Text)
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
    $Utf8NoBom = [System.Text.UTF8Encoding]::new($false)

    [System.IO.File]::WriteAllText($Tmp, $Content, $Utf8NoBom)

    if (!(Test-Path $Tmp)) {
        return @{ status = "BLOCK"; reason = "TMP_WRITE_FAILED" }
    }

    $ExpectedHash = Get-StableHash -Text $Content
    $TmpContent = [System.IO.File]::ReadAllText($Tmp, $Utf8NoBom)
    $TmpHash = Get-StableHash -Text $TmpContent

    if ($TmpHash -ne $ExpectedHash) {
        Remove-Item $Tmp -Force -ErrorAction SilentlyContinue
        return @{ status = "LOCK"; reason = "TMP_HASH_MISMATCH" }
    }

    Move-Item $Tmp $Path -Force

    if (!(Test-Path $Path)) {
        return @{ status = "BLOCK"; reason = "ATOMIC_PUBLISH_FAILED" }
    }

    $FinalContent = [System.IO.File]::ReadAllText($Path, $Utf8NoBom)
    $FinalHash = Get-StableHash -Text $FinalContent

    if ($FinalHash -ne $ExpectedHash) {
        return @{ status = "LOCK"; reason = "FINAL_HASH_MISMATCH" }
    }

    return @{
        status = "TRACE_RECORDED"
        evidence_hash = $FinalHash
        path = $Path
    }
}
