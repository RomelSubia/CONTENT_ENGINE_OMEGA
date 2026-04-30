function Invoke-MemoryEngine {
    param(
        [string]$RootPath,
        [string]$Key,
        [string]$Value
    )

    $MemDir = Join-Path $RootPath "00_SYSTEM\brain\memory"
    $MemFile = Join-Path $MemDir "MEMORY_STORE.json"

    if (!(Test-Path $MemDir)) {
        New-Item -ItemType Directory -Force -Path $MemDir | Out-Null
    }

    if (!(Test-Path $MemFile)) {
        @{} | ConvertTo-Json -Depth 10 | Set-Content $MemFile -Encoding UTF8
    }

    $Data = Get-Content $MemFile -Raw | ConvertFrom-Json

    if ($null -eq $Data) {
        $Data = @{}
    }

    $Data[$Key] = $Value

    $Data | ConvertTo-Json -Depth 10 | Set-Content $MemFile -Encoding UTF8

    return @{
        memory_status = "WRITE_OK"
        key = $Key
    }
}
