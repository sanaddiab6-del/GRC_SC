$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$snapshot = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'current.txt'))
$original = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText((Join-Path $snapshot 'manifest.json')))
$dependencies = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText((Join-Path $snapshot 'direct-dependencies.json')))
$backend = @{}
$frontend = @{}
foreach ($entry in $original) {
    if (!$entry.LiveSHA256) { continue }
    if ($entry.Path.StartsWith('backend/')) { $backend['/code/'+$entry.Path.Substring(8)] = $entry.LiveSHA256.ToLower() }
    else { $frontend['/workspace/'+$entry.Path.Substring(9)] = $entry.LiveSHA256.ToLower() }
}
foreach ($entry in $dependencies) { $backend[$entry.LivePath] = $entry.LiveSHA256.ToLower() }
$encodedBackend = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($backend|ConvertTo-Json -Compress)))
$py = @'
import base64,hashlib,json
from pathlib import Path
expected=json.loads(base64.b64decode(ENCODED))
changed=[p for p,h in expected.items() if not Path(p).is_file() or hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h]
print(json.dumps({'files_checked':len(expected),'changed':changed}))
'@
$py = $py.Replace('ENCODED',("'"+$encodedBackend+"'"))
$backendResult = $py | docker exec -i -e PYTHONDONTWRITEBYTECODE=1 amro-backend /code/.venv/bin/python -B -
if ($LASTEXITCODE -ne 0) { throw 'Backend integrity check failed' }
$encodedFrontend = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($frontend|ConvertTo-Json -Compress)))
$js = @'
const fs=require('fs'),crypto=require('crypto');
const expected=JSON.parse(Buffer.from('ENCODED','base64').toString('utf8'));
const changed=Object.entries(expected).filter(([p,h])=>!fs.existsSync(p)||crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex')!==h).map(([p])=>p);
console.log(JSON.stringify({files_checked:Object.keys(expected).length,changed}));
'@
$frontendResult = $js.Replace('ENCODED',$encodedFrontend) | docker exec -i amro-frontend node
if ($LASTEXITCODE -ne 0) { throw 'Frontend integrity check failed' }
$runtime = @()
foreach ($name in @('amro-backend','amro-frontend','amro-caddy')) {
    $raw = docker inspect $name
    if ($LASTEXITCODE -ne 0) { throw 'Container integrity inspect failed' }
    $now = (ConvertFrom-Json -InputObject ($raw -join "`n"))[0]
    $before = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText((Join-Path $snapshot ($name+'.json'))))
    $runtime += [pscustomobject]@{Name=$name;SameContainer=($now.Id -eq $before.Id);SameImage=($now.Image -eq $before.ImageId);SameStartTime=($now.State.StartedAt -eq $before.Started);Running=$now.State.Running}
}
$final = @()
foreach ($entry in @($original)+@($dependencies)) {
    $path = Join-Path $root $entry.Path
    $hash = if (Test-Path -LiteralPath $path) { (Get-FileHash -LiteralPath $path).Hash } else { $null }
    $decision = if ($entry.State -eq 'same-text') { 'existing equivalent source retained byte-for-byte' } elseif ($entry.State -eq 'repository-only') { 'repository-only source retained byte-for-byte' } elseif ($entry.State -eq 'live-only') { 'imported live-only source byte-for-byte' } elseif ($entry.Path.StartsWith('tools/')) { 'live-only case-setup flag appended; existing repository settings preserved' } else { 'repository additions retained; live behavior preserved' }
    $final += [pscustomobject]@{Path=$entry.Path;BeforeState=$entry.State;Decision=$decision;BeforeRepositorySHA256=$entry.RepositorySHA256;LiveSHA256=$entry.LiveSHA256;FinalRepositorySHA256=$hash;RepositoryOriginalUnchanged=if($entry.RepositorySHA256){$entry.RepositorySHA256 -eq $hash}else{$null}}
}
$backendObject = ConvertFrom-Json -InputObject ($backendResult -join "`n")
$frontendObject = ConvertFrom-Json -InputObject ($frontendResult -join "`n")
$unexpected = @($final|Where-Object {$_.BeforeRepositorySHA256 -and !$_.RepositoryOriginalUnchanged -and $_.Path -ne 'tools/sico_agent_release/sico_agent_release_settings.py'})
$result = [pscustomobject]@{BackendLiveSource=$backendObject;FrontendLiveSource=$frontendObject;Containers=$runtime;UnexpectedRepositoryChanges=$unexpected;FinalManifest=$final}
$utf8 = New-Object Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $snapshot 'final-integrity.json'),($result|ConvertTo-Json -Depth 8),$utf8)
if ($backendObject.changed.Count -or $frontendObject.changed.Count -or $unexpected.Count -or @($runtime|Where-Object {!$_.SameContainer -or !$_.SameImage -or !$_.SameStartTime -or !$_.Running}).Count) { throw 'Final integrity conflict; see final-integrity.json' }
Write-Output "Live backend hashes unchanged: $($backendObject.files_checked) files"
Write-Output "Live frontend hashes unchanged: $($frontendObject.files_checked) files"
Write-Output "All three named containers unchanged and running."
Write-Output "All original scoped repository files unchanged except the appended release setting."
Write-Output "Reconciliation manifest: $(Join-Path $snapshot 'final-integrity.json')"
