function Invoke-AutonomyPolicy {
    param([string]$Decision)

    switch ($Decision) {
        "ALLOW" {
            return @{
                autonomy_mode = "SAFE_EXECUTION"
                execution_permitted = $true
            }
        }
        "REQUIRE_DRY_RUN" {
            return @{
                autonomy_mode = "SIMULATION_ONLY"
                execution_permitted = $false
            }
        }
        "REQUIRE_APPROVAL" {
            return @{
                autonomy_mode = "WAIT_APPROVAL"
                execution_permitted = $false
            }
        }
        default {
            return @{
                autonomy_mode = "BLOCKED"
                execution_permitted = $false
            }
        }
    }
}
