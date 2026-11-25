param([switch]$Frontend)
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$files=@('backend/ai_onboarding/sico_case_coverage.py','backend/ai_onboarding/quality_sico_drafts_v5.py','backend/ai_onboarding/sico_ai_case_quality_views.py','backend/ai_onboarding/tests/test_scope_generation.py','backend/ai_onboarding/tests/test_sico_case_generation_queue.py','backend/ai_onboarding/tests/test_quality_all_activities.py')
$sources=@{}
foreach($file in $files){$sources[$file]=[Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $root $file)))}
$bootstrap=[IO.File]::ReadAllText((Join-Path $root '.sico-reconcile/validate_backend.py'))
$payload=@{sources=$sources;bootstrap=$bootstrap.Substring(0,$bootstrap.IndexOf('attempts ='))}|ConvertTo-Json -Depth 8 -Compress
$encoded=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($payload))
$script="import json,base64`nPAYLOAD=json.loads(base64.b64decode('$encoded'))`n"+[IO.File]::ReadAllText((Join-Path $root '.sico-shared-generation/check.py'))
$script=$script.Replace("modules=['ai_onboarding.tests.test_quality_all_activities',`n         'ai_onboarding.tests.test_quality_title_recovery',`n         'ai_onboarding.tests.test_quality_evidence_requests']", "modules=['ai_onboarding.tests.test_quality_all_activities','ai_onboarding.tests.test_scope_generation','ai_onboarding.tests.test_sico_case_generation_queue']")
$script=$script.Replace("print(json.dumps({'tests':", "from ai_onboarding.tests.test_scope_generation import ScopeGenerationTests`nprint(json.dumps({'fixture':getattr(ScopeGenerationTests,'fixture',None),'tests':")
$raw=$script|docker exec -i -e PYTHONDONTWRITEBYTECODE=1 amro-backend /code/.venv/bin/python -B -
$code=$LASTEXITCODE
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'mock-results.json'),($raw -join "`n"),(New-Object Text.UTF8Encoding($false)))
$summary=ConvertFrom-Json -InputObject ($raw -join "`n")
$summary|Select-Object tests,failures,errors,contracts_passed,provider,real_qwen_verified,deployment_performed,successful|ConvertTo-Json -Depth 5
if($code -ne 0){throw 'Scope generation mocked checks failed'}
