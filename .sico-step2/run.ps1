param([ValidateSet('unit','frontend','qwen')][string]$Mode='unit')
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$files=@(
'backend/ai_onboarding/sico_case_coverage.py',
'backend/ai_onboarding/sico_case_coverage_views.py',
'backend/ai_onboarding/sico_case_record_proposals.py',
'backend/ai_onboarding/sico_full_case_blueprint.py',
'backend/ai_onboarding/sico_case_matrix_methodology.py',
'backend/ai_onboarding/quality_sico_drafts_v5.py',
'backend/ai_onboarding/llm_provider.py',
'backend/ai_onboarding/sico_ai_case_quality_views.py',
'backend/ai_onboarding/tests/test_sico_case_generation_queue.py',
'backend/ai_onboarding/tests/test_sico_coordinated_generation.py',
'backend/ai_onboarding/tests/test_quality_evidence_requests.py',
'backend/ai_onboarding/tests/test_sico_case_coverage.py',
'backend/ai_onboarding/tests/test_sico_case_record_proposals.py',
'backend/ai_onboarding/tests/test_sico_case_matrix_methodology.py',
'backend/ai_onboarding/tests/test_sico_full_case_blueprint.py')
$map=@{}
foreach($file in $files){$map[$file]=[Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $root $file)))}
$bootstrap=[IO.File]::ReadAllText((Join-Path $root '.sico-reconcile/validate_backend.py'))
$bootstrap=$bootstrap.Substring(0,$bootstrap.IndexOf("attempts ="))
$payload=@{sources=$map;bootstrap=$bootstrap}
if($Mode -eq 'qwen' -and (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'qwen-results.jsonl'))){
    $events=@(Get-Content -LiteralPath (Join-Path $PSScriptRoot 'qwen-results.jsonl') | Where-Object { $_.StartsWith('{') } | ForEach-Object { ConvertFrom-Json -InputObject $_ })
    $source=$events|Where-Object event -eq 'source'|Select-Object -Last 1
    $accepted=@($events|Where-Object event -eq 'accepted'|ForEach-Object record)
    if($source -and $accepted.Count){$payload.demo_checkpoint=@{source=$source;accepted=$accepted}}
}
if($Mode -eq 'frontend'){
    $map=@{}
    foreach($file in @('frontend/src/routes/(app)/(internal)/sico-ai-next/+page.svelte','frontend/src/routes/(app)/(internal)/sico-ai-next/+page.server.ts','frontend/src/lib/utils/sicoGenerationPlan.ts','frontend/src/lib/components/AiOnboarding/SicoGeneratedCase.svelte')){$map[$file]=[Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $root $file)))}
    $payload=@{sources=$map;test=[Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $root 'frontend/src/lib/utils/sicoGenerationPlan.test.cjs')))}
    $unitReport=ConvertFrom-Json -InputObject ([IO.File]::ReadAllText((Join-Path $PSScriptRoot 'unit-results.jsonl')))
    $payload.coordination_fixture=$unitReport.coordination_fixture
    if(Test-Path -LiteralPath (Join-Path $PSScriptRoot 'qwen-evidence.json')){
        $payload.demo_evidence=ConvertFrom-Json -InputObject ([IO.File]::ReadAllText((Join-Path $PSScriptRoot 'qwen-evidence.json')))
    }
}
$encoded=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($payload|ConvertTo-Json -Depth 8 -Compress)))
if($Mode -eq 'frontend'){
    $script="const PAYLOAD=JSON.parse(Buffer.from('$encoded','base64').toString('utf8'));`n"+[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'frontend.cjs'))
    $raw=$script|docker exec -i amro-frontend node
}else{
    $script="import json,base64`nPAYLOAD=json.loads(base64.b64decode('$encoded'))`n"+[IO.File]::ReadAllText((Join-Path $PSScriptRoot ($Mode+'.py')))
    if($Mode -eq 'qwen'){
        $script|docker exec -i -e PYTHONDONTWRITEBYTECODE=1 amro-backend /code/.venv/bin/python -B -u - | Tee-Object -Variable raw
    }else{
        $raw=$script|docker exec -i -e PYTHONDONTWRITEBYTECODE=1 amro-backend /code/.venv/bin/python -B -u -
    }
}
$exitCode=$LASTEXITCODE
$utf8=New-Object Text.UTF8Encoding($false)
if($Mode -eq 'qwen'){
    [IO.File]::WriteAllText((Join-Path $PSScriptRoot ('qwen-attempt-'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')+'.jsonl')),($raw -join "`n"),$utf8)
    $old=Join-Path $PSScriptRoot 'qwen-results.jsonl'
    [IO.File]::AppendAllText($old,"`n"+($raw -join "`n"),$utf8)
}else{
    [IO.File]::WriteAllText((Join-Path $PSScriptRoot ($Mode+'-results.jsonl')),($raw -join "`n"),$utf8)
    if($Mode -eq 'unit'){
        $summary=ConvertFrom-Json -InputObject ($raw -join "`n")
        $summary|Select-Object compiled_modules,tests,failures,errors,skipped,successful|ConvertTo-Json -Compress
    }else{Write-Output ($raw -join "`n")}
}
if($exitCode -ne 0){throw "$Mode checks failed ($exitCode)"}
