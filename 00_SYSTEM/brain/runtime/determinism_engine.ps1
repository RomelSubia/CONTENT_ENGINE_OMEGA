function ConvertTo-StableJson {
    param([Parameter(Mandatory=$true)]$InputObject)

    function Normalize($obj) {
        if ($null -eq $obj) { return $null }

        if ($obj -is [System.Collections.IDictionary]) {
            $ordered = [ordered]@{}
            foreach ($key in @($obj.Keys | Sort-Object)) {
                $ordered[$key] = Normalize $obj[$key]
            }
            return $ordered
        }

        if ($obj -is [pscustomobject]) {
            $ordered = [ordered]@{}
            foreach ($prop in @($obj.PSObject.Properties.Name | Sort-Object)) {
                $ordered[$prop] = Normalize $obj.$prop
            }
            return $ordered
        }

        if ($obj -is [System.Collections.IEnumerable] -and $obj -isnot [string]) {
            $items = @()
            foreach ($item in $obj) { $items += Normalize $item }
            return $items
        }

        return $obj
    }

    $Normalized = Normalize $InputObject
    return ($Normalized | ConvertTo-Json -Depth 50 -Compress)
}

function Get-DeterministicHash {
    param([Parameter(Mandatory=$true)]$InputObject)

    $StableJson = ConvertTo-StableJson -InputObject $InputObject
    $Utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    $bytes = $Utf8NoBom.GetBytes($StableJson)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $hash = $sha.ComputeHash($bytes)

    return @{
        stable_json = $StableJson
        hash = ([BitConverter]::ToString($hash)).Replace("-", "").ToLowerInvariant()
    }
}

function Test-Determinism {
    param(
        [Parameter(Mandatory=$true)]$InputObject,
        [int]$Repeat = 10
    )

    $Hashes = @()

    for ($i = 0; $i -lt $Repeat; $i++) {
        $Hashes += (Get-DeterministicHash -InputObject $InputObject).hash
    }

    $Unique = @($Hashes | Select-Object -Unique)

    if ($Unique.Length -ne 1) {
        return @{
            determinism_status = "BLOCK"
            reason = "NON_DETERMINISTIC_HASH"
            hashes = $Hashes
        }
    }

    return @{
        determinism_status = "PASS"
        hash = $Unique[0]
        repeat = $Repeat
    }
}
