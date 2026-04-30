function ConvertTo-HashtableSafe {
    param($Object)

    $Hash = @{}

    if ($null -eq $Object) {
        return $Hash
    }

    foreach ($Prop in @($Object.PSObject.Properties)) {
        $Hash[$Prop.Name] = $Prop.Value
    }

    return $Hash
}

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
        "{}" | Set-Content $MemFile -Encoding UTF8
    }

    try {
        $Raw = Get-Content $MemFile -Raw
        if ([string]::IsNullOrWhiteSpace($Raw)) { $Raw = "{}" }
        $JsonObject = $Raw | ConvertFrom-Json
        $Data = ConvertTo-HashtableSafe $JsonObject
    }
    catch {
        return @{
            memory_status = "BLOCK"
            reason = "MEMORY_JSON_CORRUPTED"
        }
    }

    $Data[$Key] = $Value

    $Data | ConvertTo-Json -Depth 10 | Set-Content $MemFile -Encoding UTF8

    return @{
        memory_status = "WRITE_OK"
        key = $Key
    }
}
