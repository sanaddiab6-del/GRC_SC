$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$snapshot = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'current.txt'))
$sources = @{}
Get-ChildItem -LiteralPath (Join-Path $root 'backend/ai_onboarding') -Recurse -Filter '*.py' -File | Where-Object { $_.FullName -notmatch '[\\/](migrations|__pycache__)[\\/]' } | ForEach-Object {
    $rel = $_.FullName.Substring($root.Length+1).Replace('\','/')
    $sources[$rel] = [Convert]::ToBase64String([IO.File]::ReadAllBytes($_.FullName))
}
$overlay = Join-Path $root 'tools/sico_agent_release/sico_agent_release_settings.py'
$sources['backend/ciso_assistant/sico_agent_release_settings.py'] = [Convert]::ToBase64String([IO.File]::ReadAllBytes($overlay))
$payload = @{
    sources=$sources
    live_urls=[Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $snapshot 'live/backend/ai_onboarding/urls.py')))
    live_quality=[Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $snapshot 'live/backend/ai_onboarding/sico_ai_case_quality_views.py')))
} | ConvertTo-Json -Depth 6 -Compress
$encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($payload))
$script = "import json, base64`nPAYLOAD=json.loads(base64.b64decode('$encoded'))`n" + [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'validate_backend.py'))
$raw = $script | docker exec -i -e PYTHONDONTWRITEBYTECODE=1 amro-backend /code/.venv/bin/python -B -
$exitCode = $LASTEXITCODE
$utf8 = New-Object Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $snapshot 'backend-validation.json'),($raw -join "`n"),$utf8)
Write-Output ($raw -join "`n")
if ($exitCode -ne 0) { throw "Backend checks failed ($exitCode)" }
