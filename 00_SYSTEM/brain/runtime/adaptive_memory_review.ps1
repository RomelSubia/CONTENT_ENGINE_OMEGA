. "$PSScriptRoot\context_engine.ps1"

function Invoke-AdaptiveMemoryReview {
    param([string]$RootPath)

    $Context = Invoke-ContextEngine -RootPath $RootPath -RequestType "ADAPTIVE_REVIEW"

    if ($Context.context -eq "BLOCK") {
        return @{
            review_status = "BLOCK"
            reason = "CONTEXT_UNAVAILABLE"
        }
    }

    return @{
        review_status = "PASS"
        context = $Context.context
        entries = $Context.entries
    }
}
