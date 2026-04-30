function Invoke-StateAwareness {
    param([string]$RootPath)

    $StateFile = "$RootPath\00_SYSTEM\brain\state\BRAIN_STATE.json"

    if (!(Test-Path $StateFile)) {
        return @{
            state = "BLOCKED"
            reason = "STATE_FILE_MISSING"
        }
    }

    try {
        $State = Get-Content $StateFile -Raw | ConvertFrom-Json
    }
    catch {
        return @{
            state = "COMPROMISED"
            reason = "STATE_CORRUPTED"
        }
    }

    $repoDirty = git status --short
    if ($repoDirty) {
        return @{
            state = "BLOCKED"
            reason = "REPO_DIRTY"
        }
    }

    $local = git rev-parse HEAD
    $remote = git rev-parse "@{u}"
    if ($local -ne $remote) {
        return @{
            state = "BLOCKED"
            reason = "HEAD_MISMATCH"
        }
    }

    return @{
        state = "VALID"
        brain_layer = $State.brain_layer
        lifecycle = $State.lifecycle_state
        deterministic = $State.deterministic
    }
}
