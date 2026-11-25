$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$utf8=New-Object Text.UTF8Encoding($false)
$scope=ConvertFrom-Json -InputObject ([IO.File]::ReadAllText((Join-Path $PSScriptRoot 'milestone.json')))
$shared=ConvertFrom-Json -InputObject ([IO.File]::ReadAllText((Join-Path $root '.sico-shared-generation/milestone.json')))
$targets=@($scope.ChangedFiles|Where-Object {$_.Path -notmatch '/tests/'})
foreach($t in $targets){if((Get-FileHash -LiteralPath (Join-Path $root $t.Path)).Hash -ne $t.SHA256){throw "Milestone source changed: $($t.Path)"}}
$snapshot=Join-Path $PSScriptRoot ('activation-'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ'))
[void](New-Item -ItemType Directory -Path $snapshot)
$payload=@{paths=@($targets|Where-Object {$_.Path.StartsWith('backend/')}|ForEach-Object {'/code/'+$_.Path.Substring(8)});providerHash=(Get-FileHash -LiteralPath (Join-Path $root 'backend/ai_onboarding/llm_provider.py')).Hash.ToLower()}
$encoded=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($payload|ConvertTo-Json -Depth 6 -Compress)))
$script="import json,base64`nP=json.loads(base64.b64decode('$encoded'))`n"+@'
from pathlib import Path
import hashlib
if hashlib.sha256(Path('/code/ai_onboarding/llm_provider.py').read_bytes()).hexdigest()!=P['providerHash']: raise RuntimeError('Provider prerequisite differs; stopped')
if '/code/.venv/bin/gunicorn' not in Path('/proc/1/cmdline').read_bytes().replace(b'\0',b' ').decode(): raise RuntimeError('Unexpected master; stopped')
print(json.dumps([{'LivePath':p,'Content':base64.b64encode(Path(p).read_bytes()).decode(),'Mode':Path(p).stat().st_mode&0o777} for p in P['paths']]))
'@
$raw=$script|docker exec -i -e PYTHONDONTWRITEBYTECODE=1 amro-backend /code/.venv/bin/python -B -
if($LASTEXITCODE -ne 0){throw 'Scoped backend backup failed'}
$backend=ConvertFrom-Json -InputObject ($raw -join "`n")
$script=@'
const fs=require('fs');const p='/workspace/src/lib/utils/sicoGenerationPlan.ts';
console.log(JSON.stringify([{LivePath:p,Content:fs.readFileSync(p).toString('base64'),Mode:fs.statSync(p).mode&0o777}]));
'@
$raw=$script|docker exec -i amro-frontend node
if($LASTEXITCODE -ne 0){throw 'Scoped frontend backup failed'}
$frontend=ConvertFrom-Json -InputObject ($raw -join "`n")
$entries=@()
foreach($item in @($backend)+@($frontend)){
    $rel=if($item.LivePath.StartsWith('/code/')){'backend/'+$item.LivePath.Substring(6)}else{'frontend/'+$item.LivePath.Substring(11)}
    $bytes=[Convert]::FromBase64String($item.Content)
    $dest=Join-Path $snapshot ('live/'+$rel)
    [void](New-Item -ItemType Directory -Force -Path (Split-Path $dest))
    [IO.File]::WriteAllBytes($dest,$bytes)
    $known=@((Join-Path $root $rel),(Join-Path $scope.Rollback $rel),(Join-Path $shared.RollbackSnapshot (Split-Path $rel -Leaf)))
    $safe=$false
    foreach($candidate in $known){if((Test-Path -LiteralPath $candidate) -and [IO.File]::ReadAllText($candidate).Replace("`r`n","`n") -ceq [Text.Encoding]::UTF8.GetString($bytes).Replace("`r`n","`n")){$safe=$true;break}}
    if(!$safe){throw "Unresolved live difference: $rel; exact bytes preserved at $dest. Nothing activated."}
    $entries+=[pscustomobject]@{Path=$rel;LivePath=$item.LivePath;BackupPath=$dest;BeforeSHA256=(Get-FileHash -LiteralPath $dest).Hash.ToLower();AfterSHA256=(Get-FileHash -LiteralPath (Join-Path $root $rel)).Hash.ToLower();BeforeMode=$item.Mode;WasAbsent=$false}
}
[IO.File]::WriteAllText((Join-Path $snapshot 'activation-manifest.json'),($entries|ConvertTo-Json -Depth 6),$utf8)
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'activation-current.txt'),$snapshot,$utf8)
# Reuse the previously reviewed exact-file writer/reloader, with this directory's manifest.
[IO.File]::Copy((Join-Path $root '.sico-step2/activate.ps1'),(Join-Path $PSScriptRoot 'activate.ps1'),$true)
$instructions=@"
Exact source rollback for this activation only (verify no later edits first):
powershell -NoProfile -ExecutionPolicy Bypass -File .sico-scope-generation/activate.ps1 -Phase rollback-frontend
powershell -NoProfile -ExecutionPolicy Bypass -File .sico-scope-generation/activate.ps1 -Phase rollback-backend
powershell -NoProfile -ExecutionPolicy Bypass -File .sico-scope-generation/activate.ps1 -Phase reload
The helper verifies current deployed hashes before restoring exact backup bytes.
No database operations, startup scripts or migrations are part of rollback.
"@
[IO.File]::WriteAllText((Join-Path $snapshot 'ROLLBACK.txt'),$instructions,$utf8)
Write-Output "Prepared $($entries.Count) source files. Rollback: $snapshot"
