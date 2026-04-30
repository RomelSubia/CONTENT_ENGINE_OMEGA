function Invoke-ContextEngine {
    param(
        [string]$RootPath,
        [string]$RequestType
    )

    $MemFile = Join-Path $RootPath "00_SYSTEM\brain\memory\MEMORY_STORE.json"

    if (!(Test-Path $MemFile)) {
        return @{ context = "EMPTY" }
    }

    $Data = Get-Content $MemFile -Raw | ConvertFrom-Json

    return @{
        context = "AVAILABLE"
        entries = $Data.PSObject.Properties.Count
        last_request = $RequestType
    }
}
