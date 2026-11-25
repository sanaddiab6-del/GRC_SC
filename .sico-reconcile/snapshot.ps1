$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$snapshot = Join-Path $PSScriptRoot ('snapshot-' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ'))
[void](New-Item -ItemType Directory -Path $snapshot)
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'current.txt'), $snapshot)
$utf8 = New-Object Text.UTF8Encoding($false)
$backendExport = @'
import base64, json
from pathlib import Path
root = Path('/code')
files = sorted(p for p in (root/'ai_onboarding').rglob('*.py') if 'migrations' not in p.parts and '__pycache__' not in p.parts)
print(json.dumps({'backend/'+p.relative_to(root).as_posix():base64.b64encode(p.read_bytes()).decode() for p in files}))
'@
$frontendExport = @'
const fs = require('fs'), path = require('path');
const dirs = ['src/routes/(app)/(internal)/sico-ai-next', 'src/routes/(app)/(internal)/sico-ai', 'src/routes/fe-api/ai-onboarding', 'src/lib/components/AiOnboarding'];
const files = ['src/lib/utils/aiOnboardingProxy.ts','src/lib/utils/aiOnboardingActions.ts','src/lib/utils/sicoFrameworkReviewV3.ts'];
function visit(p) { if (!fs.existsSync(p)) return; for (const e of fs.readdirSync(p,{withFileTypes:true})) { const n=path.join(p,e.name); if(e.isDirectory()) visit(n); else if(/\.(svelte|ts|js)$/.test(n)) files.push(n); } }
dirs.forEach(visit);
process.stdout.write(JSON.stringify(Object.fromEntries(files.filter(p=>fs.existsSync(p)).map(p=>['frontend/'+p,fs.readFileSync(p).toString('base64')]))));
'@
$backendJson = $backendExport | docker exec -i amro-backend python -
if ($LASTEXITCODE -ne 0) { throw 'Backend source export failed' }
$frontendJson = $frontendExport | docker exec -i amro-frontend node
if ($LASTEXITCODE -ne 0) { throw 'Frontend source export failed' }
$liveKeys = @()
foreach ($json in @($backendJson, $frontendJson)) {
    $data = ConvertFrom-Json -InputObject ($json -join "`n")
    foreach ($entry in $data.PSObject.Properties) {
        $rel = $entry.Name
        $liveKeys += $rel
        $dest = Join-Path (Join-Path $snapshot 'live') $rel
        [void](New-Item -ItemType Directory -Force -Path (Split-Path $dest))
        [IO.File]::WriteAllBytes($dest, [Convert]::FromBase64String($entry.Value))
    }
}
$repoFiles = @()
$repoFiles += Get-ChildItem -LiteralPath (Join-Path $root 'backend/ai_onboarding') -Filter '*.py' -Recurse -File | Where-Object { $_.FullName -notmatch '[\\/](migrations|__pycache__)[\\/]' }
foreach ($rel in @('frontend/src/routes/(app)/(internal)/sico-ai-next','frontend/src/routes/(app)/(internal)/sico-ai','frontend/src/routes/fe-api/ai-onboarding','frontend/src/lib/components/AiOnboarding')) {
    $repoFiles += Get-ChildItem -LiteralPath (Join-Path $root $rel) -Recurse -File | Where-Object { $_.Extension -in '.svelte','.ts','.js' }
}
foreach ($rel in @('frontend/src/lib/utils/aiOnboardingProxy.ts','frontend/src/lib/utils/aiOnboardingActions.ts','frontend/src/lib/utils/sicoFrameworkReviewV3.ts')) { $repoFiles += Get-Item -LiteralPath (Join-Path $root $rel) }
foreach ($file in $repoFiles) {
    $rel = $file.FullName.Substring($root.Length+1)
    $dest = Join-Path (Join-Path $snapshot 'repository') $rel
    [void](New-Item -ItemType Directory -Force -Path (Split-Path $dest))
    [IO.File]::Copy($file.FullName, $dest, $false)
}
$manifest = @()
$allKeys = @($liveKeys + @($repoFiles | ForEach-Object { $_.FullName.Substring($root.Length+1).Replace('\','/') })) | Sort-Object -Unique
foreach ($rel in $allKeys) {
    $repo = Join-Path (Join-Path $snapshot 'repository') $rel
    $live = Join-Path (Join-Path $snapshot 'live') $rel
    $repoHash = if (Test-Path -LiteralPath $repo) { (Get-FileHash -LiteralPath $repo -Algorithm SHA256).Hash } else { $null }
    $liveHash = if (Test-Path -LiteralPath $live) { (Get-FileHash -LiteralPath $live -Algorithm SHA256).Hash } else { $null }
    $sameText = $repoHash -and $liveHash -and ([IO.File]::ReadAllText($repo).Replace("`r`n","`n") -ceq [IO.File]::ReadAllText($live).Replace("`r`n","`n"))
    $state = if (!$repoHash) { 'live-only' } elseif (!$liveHash) { 'repository-only' } elseif ($sameText) { 'same-text' } else { 'different' }
    $manifest += [pscustomobject]@{Path=$rel; State=$state; RepositorySHA256=$repoHash; LiveSHA256=$liveHash}
}
[IO.File]::WriteAllText((Join-Path $snapshot 'manifest.json'), ($manifest | ConvertTo-Json -Depth 4), $utf8)
[IO.File]::WriteAllText((Join-Path $snapshot 'git-status-before.txt'), ((git status --short) -join "`n"), $utf8)
[IO.File]::WriteAllText((Join-Path $snapshot 'git-head.txt'), ((git rev-parse HEAD) -join "`n"), $utf8)
$headZip = Join-Path $snapshot 'head-scoped.zip'
git archive --format=zip --output $headZip HEAD backend/ai_onboarding 'frontend/src/routes/(app)/(internal)/sico-ai-next' 'frontend/src/routes/(app)/(internal)/sico-ai' frontend/src/routes/fe-api/ai-onboarding frontend/src/lib/components/AiOnboarding frontend/src/lib/utils/aiOnboardingProxy.ts frontend/src/lib/utils/aiOnboardingActions.ts frontend/src/lib/utils/sicoFrameworkReviewV3.ts
if ($LASTEXITCODE -ne 0) { throw 'HEAD snapshot failed' }
foreach ($name in @('amro-backend','amro-frontend','amro-caddy')) {
    $raw = docker inspect $name
    if ($LASTEXITCODE -ne 0) { throw 'Container inspection failed' }
    $item = (ConvertFrom-Json -InputObject ($raw -join "`n"))[0]
    $meta = [pscustomobject]@{Name=$item.Name; Id=$item.Id; Image=$item.Config.Image; ImageId=$item.Image; Started=$item.State.StartedAt; WorkingDir=$item.Config.WorkingDir; Project=$item.Config.Labels.'com.docker.compose.project'; Mounts=$item.Mounts}
    [IO.File]::WriteAllText((Join-Path $snapshot ($name+'.json')), ($meta | ConvertTo-Json -Depth 6), $utf8)
}
Write-Output "SNAPSHOT=$snapshot"
$manifest | Group-Object State | Select-Object Name,Count | Format-Table
$manifest | Where-Object State -ne 'same-text' | Select-Object Path,State | Format-Table -AutoSize
