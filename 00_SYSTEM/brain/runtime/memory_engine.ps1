function Invoke-MemoryEngine {
    param(
        [string]$RootPath,
        [string]$Key,
        [string]$Value
    )

    $MemFile = Join-Path $RootPath "00_SYSTEM\brain\memory\MEMORY_STORE.json"

    if (!(Test-Path $MemFile)) {
        $Init = @{}
        $Init | ConvertTo-Json -Depth 10 | Set-Content $MemFile -Encoding UTF8
    }

    $Data = Get-Content $MemFile -Raw | ConvertFrom-Json

    $Data[$Key] = $Value

    $Data | ConvertTo-Json -Depth 10 | Set-Content $MemFile -Encoding UTF8

    return @{
        memory_status = "WRITE_OK"
        key = $Key
    }
}
