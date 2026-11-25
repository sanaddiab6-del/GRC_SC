$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$rollback=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'current.txt'))
$files=@(
'backend/ai_onboarding/llm_provider.py',
'backend/ai_onboarding/quality_sico_drafts_v5.py',
'backend/ai_onboarding/sico_ai_case_quality_views.py',
'backend/ai_onboarding/sico_case_coverage.py',
'backend/ai_onboarding/sico_case_record_proposals.py',
'frontend/src/routes/(app)/(internal)/sico-ai-next/+page.server.ts',
'frontend/src/routes/(app)/(internal)/sico-ai-next/+page.svelte',
'frontend/src/lib/utils/sicoGenerationPlan.ts',
'frontend/src/lib/components/AiOnboarding/SicoGeneratedCase.svelte',
'backend/ai_onboarding/tests/test_sico_case_generation_queue.py',
'backend/ai_onboarding/tests/test_sico_coordinated_generation.py',
'frontend/src/lib/utils/sicoGenerationPlan.test.cjs')
$manifest=@()
foreach($file in $files){
    $before=Join-Path $rollback $file
    $manifest+=[pscustomobject]@{Path=$file;NewFile=!(Test-Path -LiteralPath $before);BeforeSHA256=if(Test-Path -LiteralPath $before){(Get-FileHash -LiteralPath $before).Hash}else{$null};AfterSHA256=(Get-FileHash -LiteralPath (Join-Path $root $file)).Hash}
}
$backend=ConvertFrom-Json -InputObject ([IO.File]::ReadAllText((Join-Path $PSScriptRoot 'unit-results.jsonl')))
$frontend=ConvertFrom-Json -InputObject ([IO.File]::ReadAllText((Join-Path $PSScriptRoot 'frontend-results.jsonl')))
$evidence=ConvertFrom-Json -InputObject ([IO.File]::ReadAllText((Join-Path $PSScriptRoot 'qwen-evidence.json')))
git -c core.autocrlf=false diff --check -- backend/ai_onboarding/llm_provider.py backend/ai_onboarding/quality_sico_drafts_v5.py backend/ai_onboarding/sico_ai_case_quality_views.py 'frontend/src/routes/(app)/(internal)/sico-ai-next/+page.server.ts' 'frontend/src/routes/(app)/(internal)/sico-ai-next/+page.svelte'
if($LASTEXITCODE -ne 0){throw 'Scoped whitespace check failed'}
$result=[pscustomobject]@{
    Implemented=@('Framework-driven task queue connected to Build a GRC case','All authorized requirements scheduled; nonuniform activity counts and explicit parent dependencies','Focus fields forwarded and independently validated against authorized source','16 existing activities and checkpoint schema retained; source identity survives restore','Searchable case board, category navigation, linked record inspector, proposed full matrix and honest coverage counts','Type/asset/relationship checks, distinct narratives, accountable roles and observable control tests','Native SICO treatment choices and conservative Threat/Vulnerability model proposals','Provider disconnect sanitization and no synthetic fallback')
    ExactChangedSourceFiles=$manifest
    RollbackSnapshot=$rollback
    BackendTests=($backend|Select-Object compiled_modules,tests,failures,errors,skipped,successful)
    FrontendTests=$frontend
    ActualQwen=[pscustomobject]@{Model=$evidence.Model;Framework=$evidence.Framework;AuthorizedRequirementCount=$evidence.AuthorizedRequirementCount;PlannedRecordCount=$evidence.PlannedRecordCount;AcceptedRecords=@($evidence.AcceptedModelRecords).Count;FullChainDemonstrated=$evidence.FullChainDemonstrated;GeneratedNarrativesUnchanged=$evidence.GeneratedNarrativesUnchanged;ModelFieldsValidated=$evidence.ModelFieldsValidatedAgainstExistingSicoModels;EvidenceFile='.sico-step2/qwen-evidence.json';RejectedAttemptsPreserved=$true}
    RuntimeDeploymentPerformed=$false
    FullFrontendBuildPerformed=$false
    BusinessRecordWritesPerformed=$false
    Remaining=@('Deployment of the tested repository frontend/backend is required; running interface unchanged','End-to-end Qwen generation through all 16 activities has not been demonstrated','Evidence-backed requirement assessment and complete risk scoring against an approved matrix have not been demonstrated','Approved creation through existing tenant-scoped writers has not been demonstrated','Generated prose still requires professional human verification; lexical/relationship guards do not establish substantive correctness')
}
$utf8=New-Object Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'changed-files.json'),($manifest|ConvertTo-Json -Depth 5),$utf8)
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'step2-result.json'),($result|ConvertTo-Json -Depth 16),$utf8)
Write-Output "Changed source/test files: $($manifest.Count)"
Write-Output "Backend tests: $($backend.tests), pass=$($backend.successful)"
Write-Output "Frontend checks: $($frontend.checks), pass=$($frontend.successful)"
Write-Output "Genuine accepted Qwen records: $(@($evidence.AcceptedModelRecords).Count); chain validated=$($evidence.FullChainDemonstrated)"
Write-Output 'Deployment required. No business record writes or full build.'
