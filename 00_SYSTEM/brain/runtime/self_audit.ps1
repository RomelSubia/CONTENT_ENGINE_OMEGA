function Invoke-SelfAudit {
    param([string]$RootPath)

    $Result = @{
        status = "PASS"
        checks = @()
        failed = @()
    }

    function Check($name, $condition){
        if ($condition) {
            $Result.checks += $name
        } else {
            $Result.failed += $name
            $Result.status = "BLOCK"
        }
    }

    Check "ROOT_EXISTS" (Test-Path $RootPath)
    Check "GIT_FOLDER_EXISTS" (Test-Path "$RootPath\.git")

    $gitStatus = git status --short
    Check "REPO_CLEAN" (-not $gitStatus)

    $local = git rev-parse HEAD
    $remote = git rev-parse "@{u}"
    Check "HEAD_SYNC" ($local -eq $remote)

    Check "BRAIN_STATE_EXISTS" (Test-Path "$RootPath\00_SYSTEM\brain\state\BRAIN_STATE.json")
    Check "POLICY_REGISTRY_EXISTS" (Test-Path "$RootPath\00_SYSTEM\brain\policies\POLICY_REGISTRY.json")

    if ($Result.failed.Count -gt 0) {
        $Result.status = "BLOCK"
    }

    return $Result
}
