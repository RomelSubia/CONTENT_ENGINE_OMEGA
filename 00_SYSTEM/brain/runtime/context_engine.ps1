function Invoke-ContextEngine {
    param(
        [string]$RootPath,
        [string]$RequestType
    )

    $MemFile = Join-Path $RootPath "00_SYSTEM\brain\memory\MEMORY_STORE.json"

    if (!(Test-Path $MemFile)) {
        return @{
            context = "EMPTY"
            entries = 0
            last_request = $RequestType
        }
    }

    try {
        $Raw = Get-Content $MemFile -Raw
        if ([string]::IsNullOrWhiteSpace($Raw)) { $Raw = "{}" }

        $Data = $Raw | ConvertFrom-Json
        $Props = @($Data.PSObject.Properties)

        return @{
            context = "AVAILABLE"
            entries = $Props.Length
            last_request = $RequestType
        }
    }
    catch {
        return @{
            context = "BLOCK"
            reason = "CONTEXT_READ_FAILED"
        }
    }
}
