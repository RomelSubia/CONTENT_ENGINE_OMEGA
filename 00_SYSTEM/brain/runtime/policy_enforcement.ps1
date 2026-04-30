function Invoke-PolicyEnforcement {
    param(
        [string]$RootPath,
        [string]$RequestType = "AUDIT"
    )

    $PolicyFile = Join-Path $RootPath "00_SYSTEM\brain\policies\POLICY_REGISTRY.json"

    if (!(Test-Path $PolicyFile)) {
        return @{
            policy_result = "POLICY_BLOCK"
            violated_policies = @("POLICY_REGISTRY_MISSING")
        }
    }

    try {
        $PolicyRegistry = Get-Content $PolicyFile -Raw | ConvertFrom-Json
    }
    catch {
        return @{
            policy_result = "POLICY_BLOCK"
            violated_policies = @("POLICY_REGISTRY_CORRUPTED")
        }
    }

    $Violations = @()

    $gitStatus = git status --short
    if ($gitStatus) {
        $Violations += "NO_DIRTY_REPO_EXECUTION"
    }

    if ($RequestType -eq "MANUAL_CONNECTION") {
        $Violations += "NO_MANUAL_CONNECTION_BEFORE_BRAIN_READY"
    }

    if ($RequestType -eq "EXECUTION") {
        $Violations += "NO_EXECUTION_WITHOUT_VALIDATION"
    }

    if ($RequestType -eq "MUTATION") {
        $Violations += "NO_MUTATION_WITHOUT_APPROVAL"
    }

    if ($RequestType -eq "COMMIT") {
        $Violations += "NO_COMMIT_WITHOUT_AUDIT"
    }

    $DisabledCritical = @($PolicyRegistry.policies | Where-Object {
        $_.enabled -ne $true -and $_.severity -in @("BLOCK","LOCK")
    })

    if ($DisabledCritical.Length -gt 0) {
        return @{
            policy_result = "POLICY_LOCK"
            violated_policies = @("CRITICAL_POLICY_DISABLED")
        }
    }

    if ($Violations.Length -gt 0) {
        return @{
            policy_result = "POLICY_BLOCK"
            violated_policies = $Violations
        }
    }

    return @{
        policy_result = "POLICY_PASS"
        violated_policies = @()
    }
}
