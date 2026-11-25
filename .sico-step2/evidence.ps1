$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$events=@(Get-Content -LiteralPath (Join-Path $PSScriptRoot 'qwen-results.jsonl')|Where-Object {$_.StartsWith('{')}|ForEach-Object {ConvertFrom-Json -InputObject $_})
$source=$events|Where-Object event -eq 'source'|Select-Object -Last 1
$accepted=@{}
foreach($event in $events){
    if($event.event -eq 'accepted'){$accepted[$event.record.draft.draft_reference]=$event.record}
    # Keep the latest raw candidate; the final Python validator decides whether
    # it is valid. A rejection of an older candidate must not erase a later one.
}
$evidence=@{Model=$source.model;Organization=$source.organization;Framework=$source.framework;FrameworkId=$source.framework_id;SourceDigest=$source.source_digest;AuthorizedRequirementCount=$source.authorized_requirement_count;PlannedRecordCount=$source.planned_records;AcceptedModelRecords=@($accepted.Values|Sort-Object activity_number);RejectedAttempts=@($events|Where-Object {$_.event -in 'rejected','review_rejected'});BusinessRecordsWritten=$false}
$map=@{}
foreach($file in @('backend/ai_onboarding/quality_sico_drafts_v5.py','backend/ai_onboarding/sico_case_coverage.py','backend/ai_onboarding/sico_case_record_proposals.py')){$map[$file]=[Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $root $file)))}
$bootstrap=[IO.File]::ReadAllText((Join-Path $root '.sico-reconcile/validate_backend.py'))
$bootstrap=$bootstrap.Substring(0,$bootstrap.IndexOf('attempts ='))
$payload=@{sources=$map;bootstrap=$bootstrap;evidence=$evidence}
$encoded=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($payload|ConvertTo-Json -Depth 16 -Compress)))
$script="import json,base64`nPAYLOAD=json.loads(base64.b64decode('$encoded'))`n"+[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'verify_evidence.py'))
$raw=$script|docker exec -i -e PYTHONDONTWRITEBYTECODE=1 amro-backend /code/.venv/bin/python -B -
if($LASTEXITCODE -ne 0){throw 'Evidence verification failed'}
$result=ConvertFrom-Json -InputObject ($raw -join "`n")
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'qwen-evidence.json'),($result|ConvertTo-Json -Depth 16),(New-Object Text.UTF8Encoding($false)))
$result|Select-Object Model,Organization,AuthorizedRequirementCount,PlannedRecordCount,FullChainDemonstrated,GeneratedNarrativesUnchanged,ModelFieldsValidatedAgainstExistingSicoModels|ConvertTo-Json
