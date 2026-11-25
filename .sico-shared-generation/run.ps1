$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$sources=@{}
foreach($file in @('backend/ai_onboarding/quality_sico_drafts_v5.py','backend/ai_onboarding/sico_ai_case_quality_views.py','backend/ai_onboarding/tests/test_quality_all_activities.py','backend/ai_onboarding/tests/test_quality_title_recovery.py','backend/ai_onboarding/tests/test_quality_evidence_requests.py')){
    $sources[$file]=[Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $root $file)))
}
$bootstrap=[IO.File]::ReadAllText((Join-Path $root '.sico-reconcile/validate_backend.py'))
$payload=@{sources=$sources;bootstrap=$bootstrap.Substring(0,$bootstrap.IndexOf('attempts ='))}|ConvertTo-Json -Depth 8 -Compress
$encoded=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($payload))
$script="import json,base64`nPAYLOAD=json.loads(base64.b64decode('$encoded'))`n"+[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'check.py'))
$raw=$script|docker exec -i -e PYTHONDONTWRITEBYTECODE=1 amro-backend /code/.venv/bin/python -B -
$code=$LASTEXITCODE
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'mock-results.json'),($raw -join "`n"),(New-Object Text.UTF8Encoding($false)))
Write-Output ($raw -join "`n")
if($code -ne 0){throw 'Mocked contract tests failed'}
