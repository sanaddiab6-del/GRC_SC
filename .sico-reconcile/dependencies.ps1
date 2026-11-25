$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$snapshot = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'current.txt'))
$sourceMap = @{}
Get-ChildItem -LiteralPath (Join-Path $snapshot 'repository/backend/ai_onboarding') -Filter '*.py' -File | ForEach-Object {
    $sourceMap['backend/ai_onboarding/'+$_.Name] = [Convert]::ToBase64String([IO.File]::ReadAllBytes($_.FullName))
}
$payload = @{repository=$sourceMap} | ConvertTo-Json -Depth 5 -Compress
$encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($payload))
$script = "import json, base64`nPAYLOAD=json.loads(base64.b64decode('$encoded'))`n" + [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'dependencies.py'))
$raw = $script | docker exec -i amro-backend python -
if ($LASTEXITCODE -ne 0) { throw 'Dependency export failed' }
$data = ConvertFrom-Json -InputObject ($raw -join "`n")
$rows = @()
foreach ($entry in $data.PSObject.Properties) {
    $rel = 'backend/'+$entry.Name
    if ($entry.Name -eq 'sico-agent-start.sh') { $rel = 'tools/sico_agent_release/sico-agent-start.sh' }
    if ($entry.Name -eq 'ciso_assistant/sico_agent_release_settings.py') { $rel = 'tools/sico_agent_release/sico_agent_release_settings.py' }
    $liveDest = Join-Path (Join-Path $snapshot 'direct-dependencies/live') $rel
    [void](New-Item -ItemType Directory -Path (Split-Path $liveDest) -Force)
    [IO.File]::WriteAllBytes($liveDest,[Convert]::FromBase64String($entry.Value.content))
    $repo = Join-Path $root $rel
    $state = 'live-only'
    if (Test-Path -LiteralPath $repo) {
        $repoDest = Join-Path (Join-Path $snapshot 'direct-dependencies/repository') $rel
        [void](New-Item -ItemType Directory -Path (Split-Path $repoDest) -Force)
        [IO.File]::Copy($repo,$repoDest,$false)
        $state = if ([IO.File]::ReadAllText($repo).Replace("`r`n","`n") -ceq [IO.File]::ReadAllText($liveDest).Replace("`r`n","`n")) { 'same-text' } else { 'different' }
    }
    $rows += [pscustomobject]@{Path=$rel; LivePath=('/code/'+$entry.Name); State=$state; LiveSHA256=$entry.Value.sha256; RepositorySHA256=if(Test-Path -LiteralPath $repo){(Get-FileHash -LiteralPath $repo).Hash}else{$null}}
}
$utf8 = New-Object Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $snapshot 'direct-dependencies.json'),($rows|ConvertTo-Json -Depth 4),$utf8)
$rows | Format-Table Path,State -AutoSize
