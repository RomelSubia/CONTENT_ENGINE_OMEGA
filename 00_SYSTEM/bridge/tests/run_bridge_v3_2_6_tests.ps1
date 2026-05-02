$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

. "00_SYSTEM\bridge\rule_extractor\manual_rule_extractor_v3_2_6.ps1"
. "00_SYSTEM\bridge\conflict_detector\manual_brain_conflict_detector_v3_2_6.ps1"
. "00_SYSTEM\bridge\governance\bridge_v3_2_6_validator.ps1"

$Root="D:\CONTENT_ENGINE_OMEGA"
$FixtureRoot=Join-Path $Root "00_SYSTEM\bridge\tests\fixtures\v3_2_6"

function Assert-Test {
    param([string]$Name,[bool]$Condition,[string]$Details="")

    if (-not $Condition) {
        throw "TEST_FAILED: $Name :: $Details"
    }

    Write-Host "[OK] $Name" -ForegroundColor Green
}

function Get-FixtureText($Name) {
    return Get-Content -LiteralPath (Join-Path $FixtureRoot $Name) -Raw
}

$t1=Get-FixtureText "manual_valid_rules.txt"
$r1=Build-ManualRulesRegistryV326 -SourceText $t1 -SourceName "fixture/manual_valid_rules.txt" -SourceHash "fixturehashvalid"
$c1=Find-ManualBrainConflictsV326 -RuleRegistry $r1 -RootPath $Root
Assert-Test "T001 valid_rules extracts rules" ($r1.rules_count -ge 10) "rules=$($r1.rules_count)"
Assert-Test "T001 valid_rules no LOCK" ($c1.status -ne "LOCK") $c1.reason

$t2=Get-FixtureText "manual_no_rules.txt"
$r2=Build-ManualRulesRegistryV326 -SourceText $t2 -SourceName "fixture/manual_no_rules.txt" -SourceHash "fixturehashnorules"
Assert-Test "T002 no_rules blocks or review" ($r2.status -eq "BLOCK" -or $r2.status -eq "REQUIRE_REVIEW") $r2.status

$t3=Get-FixtureText "manual_capa9_positive.txt"
$r3=Build-ManualRulesRegistryV326 -SourceText $t3 -SourceName "fixture/manual_capa9_positive.txt" -SourceHash "fixturehashcapa9pos"
$c3=Find-ManualBrainConflictsV326 -RuleRegistry $r3 -RootPath $Root
Assert-Test "T003 capa9_positive blocks" ($c3.status -eq "BLOCK") $c3.status

$t4=Get-FixtureText "manual_capa9_negative.txt"
$r4=Build-ManualRulesRegistryV326 -SourceText $t4 -SourceName "fixture/manual_capa9_negative.txt" -SourceHash "fixturehashcapa9neg"
$c4=Find-ManualBrainConflictsV326 -RuleRegistry $r4 -RootPath $Root
Assert-Test "T004 capa9_negative not block" ($c4.status -ne "BLOCK" -and $c4.status -ne "LOCK") $c4.status

$t5=Get-FixtureText "manual_brain_mutation.txt"
$r5=Build-ManualRulesRegistryV326 -SourceText $t5 -SourceName "fixture/manual_brain_mutation.txt" -SourceHash "fixturehashbrain"
$c5=Find-ManualBrainConflictsV326 -RuleRegistry $r5 -RootPath $Root
Assert-Test "T005 brain_mutation lock/block" ($c5.status -eq "LOCK" -or $c5.status -eq "BLOCK") $c5.status

$t6=Get-FixtureText "manual_external_execution.txt"
$r6=Build-ManualRulesRegistryV326 -SourceText $t6 -SourceName "fixture/manual_external_execution.txt" -SourceHash "fixturehashexternal"
$c6=Find-ManualBrainConflictsV326 -RuleRegistry $r6 -RootPath $Root
Assert-Test "T006 external_execution blocks" ($c6.status -eq "BLOCK") $c6.status

$t7=Get-FixtureText "manual_fail_closed_valid.txt"
$scan7=Test-ManualContaminationV326 -ManualText $t7
Assert-Test "T007 fail_closed_valid not contamination" ($scan7.status -eq "PASS") $scan7.status

$t8=Get-FixtureText "manual_console_noise.txt"
$scan8=Test-ManualContaminationV326 -ManualText $t8
Assert-Test "T008 console_noise blocks" ($scan8.status -eq "BLOCK") $scan8.status

$t9=Get-FixtureText "manual_duplicate_rules.txt"
$r9=Build-ManualRulesRegistryV326 -SourceText $t9 -SourceName "fixture/manual_duplicate_rules.txt" -SourceHash "fixturehashdup"
$c9=Find-ManualBrainConflictsV326 -RuleRegistry $r9 -RootPath $Root
Assert-Test "T009 duplicate_rules warning or review" ($c9.warnings_count -ge 1 -or $r9.status -eq "REQUIRE_REVIEW") "warnings=$($c9.warnings_count)"

$t10=Get-FixtureText "manual_contradictory_rules.txt"
$r10=Build-ManualRulesRegistryV326 -SourceText $t10 -SourceName "fixture/manual_contradictory_rules.txt" -SourceHash "fixturehashcontra"
$c10=Find-ManualBrainConflictsV326 -RuleRegistry $r10 -RootPath $Root
Assert-Test "T010 contradictory_rules not pass clean" ($c10.status -ne "PASS") $c10.status

Write-Host "[OK] BRIDGE V3.2.6 TEST HARNESS PASS" -ForegroundColor Green