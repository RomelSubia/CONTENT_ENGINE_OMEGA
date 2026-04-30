function Invoke-DecisionEngine {
    param(
        [Parameter(Mandatory=$true)][string]$RequestType,
        [Parameter(Mandatory=$true)][hashtable]$Layer4Result
    )

    if ($Layer4Result.result -ne "PASS") {
        return @{
            decision = "BLOCK"
            reason = "LAYER4_NOT_VALID"
            risk_level = "HIGH"
            confidence = 1.0
        }
    }

    switch ($RequestType) {
        "AUDIT" {
            return @{
                decision = "ALLOW"
                reason = "AUDIT_SAFE"
                risk_level = "LOW"
                confidence = 1.0
            }
        }
        "DRY_RUN" {
            return @{
                decision = "ALLOW"
                reason = "DRY_RUN_SAFE"
                risk_level = "LOW"
                confidence = 1.0
            }
        }
        "EXECUTION" {
            return @{
                decision = "REQUIRE_DRY_RUN"
                reason = "EXECUTION_REQUIRES_DRY_RUN_FIRST"
                risk_level = "MEDIUM"
                confidence = 1.0
            }
        }
        "MUTATION" {
            return @{
                decision = "REQUIRE_APPROVAL"
                reason = "MUTATION_REQUIRES_APPROVAL"
                risk_level = "HIGH"
                confidence = 1.0
            }
        }
        "COMMIT" {
            return @{
                decision = "REQUIRE_AUDIT"
                reason = "COMMIT_REQUIRES_AUDIT"
                risk_level = "HIGH"
                confidence = 1.0
            }
        }
        "MANUAL_CONNECTION" {
            return @{
                decision = "BLOCK"
                reason = "MANUAL_CONNECTION_BLOCKED_UNTIL_BRAIN_READY"
                risk_level = "CRITICAL"
                confidence = 1.0
            }
        }
        default {
            return @{
                decision = "ESCALATE"
                reason = "UNKNOWN_REQUEST_TYPE"
                risk_level = "MEDIUM"
                confidence = 0.5
            }
        }
    }
}
