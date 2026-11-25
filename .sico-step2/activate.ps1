param([ValidateSet('prepare','backend','reload','frontend','rollback-backend','rollback-frontend')][string]$Phase='prepare')
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$utf8=New-Object Text.UTF8Encoding($false)
function Run-Backend($code,$payload){
    $encoded=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($payload|ConvertTo-Json -Depth 12 -Compress)))
    $script="import json,base64`nPAYLOAD=json.loads(base64.b64decode('$encoded'))`n"+$code
    $raw=$script|docker exec -i -e PYTHONDONTWRITEBYTECODE=1 amro-backend /code/.venv/bin/python -B -
    if($LASTEXITCODE -ne 0){throw 'Backend activation operation failed; stopped'}
    return ConvertFrom-Json -InputObject ($raw -join "`n")
}
function Run-Frontend($code,$payload){
    $encoded=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($payload|ConvertTo-Json -Depth 12 -Compress)))
    $script="const PAYLOAD=JSON.parse(Buffer.from('$encoded','base64').toString('utf8'));`n"+$code
    $raw=$script|docker exec -i amro-frontend node
    if($LASTEXITCODE -ne 0){throw 'Frontend activation operation failed; stopped'}
    return ConvertFrom-Json -InputObject ($raw -join "`n")
}
if($Phase -eq 'prepare'){
    $manifest=ConvertFrom-Json -InputObject ([IO.File]::ReadAllText((Join-Path $PSScriptRoot 'changed-files.json')))
    $rollback=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'current.txt'))
    $step1=Join-Path $root '.sico-reconcile/snapshot-20261124T090306Z'
    $targets=@($manifest|Where-Object {$_.Path -notmatch '/tests/|\.test\.cjs$'})
    foreach($file in $targets){if((Get-FileHash -LiteralPath (Join-Path $root $file.Path)).Hash -ne $file.AfterSHA256){throw "Tested manifest hash changed: $($file.Path)"}}
    foreach($rel in @('backend/ai_onboarding/urls.py','backend/ai_onboarding/sico_case_coverage_views.py','backend/ai_onboarding/sico_full_case_blueprint.py','backend/ai_onboarding/sico_case_matrix_methodology.py')){
        if((Get-FileHash -LiteralPath (Join-Path $root $rel)).Hash -ne (Get-FileHash -LiteralPath (Join-Path $step1 ('repository/'+$rel))).Hash){throw "Required preserved dependency changed: $rel"}
        $targets+=[pscustomobject]@{Path=$rel;AfterSHA256=(Get-FileHash -LiteralPath (Join-Path $root $rel)).Hash}
    }
    $snapshot=Join-Path $PSScriptRoot ('activation-'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ'))
    [void](New-Item -ItemType Directory -Path $snapshot)
    [IO.File]::WriteAllText((Join-Path $PSScriptRoot 'activation-current.txt'),$snapshot,$utf8)
    $backendPaths=@($targets|Where-Object {$_.Path.StartsWith('backend/')}|ForEach-Object { '/code/'+$_.Path.Substring(8) })
    $frontendPaths=@($targets|Where-Object {$_.Path.StartsWith('frontend/')}|ForEach-Object { '/workspace/'+$_.Path.Substring(9) })
    $backend=Run-Backend @'
import hashlib,os
from pathlib import Path
entries=[]
for name in PAYLOAD['paths']:
    p=Path(name)
    raw=p.read_bytes() if p.is_file() else None
    entries.append({'LivePath':name,'Content':base64.b64encode(raw).decode() if raw is not None else None,'SHA256':hashlib.sha256(raw).hexdigest() if raw is not None else None,'Mode':(p.stat().st_mode&0o777) if raw is not None else None})
master=Path('/proc/1/cmdline').read_bytes().replace(b'\0',b' ').decode()
if '/code/.venv/bin/gunicorn' not in master: raise RuntimeError('Expected Gunicorn master not present')
print(json.dumps(entries))
'@ @{paths=$backendPaths}
    $frontend=Run-Frontend @'
const fs=require('fs'),crypto=require('crypto');
console.log(JSON.stringify(PAYLOAD.paths.map(name=>{const raw=fs.existsSync(name)?fs.readFileSync(name):null;return {LivePath:name,Content:raw===null?null:raw.toString('base64'),SHA256:raw===null?null:crypto.createHash('sha256').update(raw).digest('hex'),Mode:raw===null?null:fs.statSync(name).mode&0o777}})));
'@ @{paths=$frontendPaths}
    $entries=@()
    foreach($entry in @($backend)+@($frontend)){
        $rel=if($entry.LivePath.StartsWith('/code/')){'backend/'+$entry.LivePath.Substring(6)}else{'frontend/'+$entry.LivePath.Substring(11)}
        $target=Join-Path $root $rel
        $desired=[IO.File]::ReadAllBytes($target)
        $backup=Join-Path $snapshot ('live/'+$rel)
        if($null -ne $entry.Content){
            [void](New-Item -ItemType Directory -Force -Path (Split-Path $backup))
            $live=[Convert]::FromBase64String($entry.Content)
            [IO.File]::WriteAllBytes($backup,$live)
            $allowed=@($target,(Join-Path $rollback $rel),(Join-Path $step1 ('live/'+$rel)))
            $known=$false
            foreach($path in $allowed){if((Test-Path -LiteralPath $path) -and ([IO.File]::ReadAllText($path).Replace("`r`n","`n") -ceq [Text.Encoding]::UTF8.GetString($live).Replace("`r`n","`n"))){$known=$true;break}}
            if(!$known){throw "Unresolved live difference; no source activated: $rel. Exact live backup: $backup"}
        }
        $entries+=[pscustomobject]@{Path=$rel;LivePath=$entry.LivePath;BackupPath=if($null -ne $entry.Content){$backup}else{$null};BeforeSHA256=$entry.SHA256;BeforeMode=$entry.Mode;AfterSHA256=(Get-FileHash -LiteralPath $target).Hash.ToLower();WasAbsent=($null -eq $entry.Content)}
    }
    [IO.File]::WriteAllText((Join-Path $snapshot 'activation-manifest.json'),($entries|ConvertTo-Json -Depth 6),$utf8)
    Write-Output "Prepared $($entries.Count) source targets; all live versions known or absent."
    Write-Output "Exact rollback snapshot: $snapshot"
    exit
}
$snapshot=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'activation-current.txt'))
$entries=ConvertFrom-Json -InputObject ([IO.File]::ReadAllText((Join-Path $snapshot 'activation-manifest.json')))
if($Phase -eq 'reload'){
    Run-Backend @'
import os,signal
from pathlib import Path
if '/code/.venv/bin/gunicorn' not in Path('/proc/1/cmdline').read_bytes().replace(b'\0',b' ').decode(): raise RuntimeError('Gunicorn master changed; stopped')
os.kill(1,signal.SIGHUP)
print(json.dumps({'backend_workers_reload_requested':True,'container_restarted':False}))
'@ @{} | ConvertTo-Json -Compress
    exit
}
$isBackend=$Phase -match 'backend$'
$restore=$Phase.StartsWith('rollback-')
$selected=@($entries|Where-Object {if($isBackend){$_.Path.StartsWith('backend/')}else{$_.Path.StartsWith('frontend/')}})
$payloadFiles=@()
foreach($entry in $selected){
    $source=if($restore){$entry.BackupPath}else{Join-Path $root $entry.Path}
    $content=if($source){[Convert]::ToBase64String([IO.File]::ReadAllBytes($source))}else{$null}
    if(!$restore -and (Get-FileHash -LiteralPath $source).Hash.ToLower() -ne $entry.AfterSHA256){throw "Source changed since prepare: $($entry.Path)"}
    $payloadFiles+=@{path=$entry.LivePath;content=$content;expected=if($restore){$entry.AfterSHA256}else{$entry.BeforeSHA256};mode=if($entry.BeforeMode){$entry.BeforeMode}else{420}}
}
if($isBackend){
    $result=Run-Backend @'
import hashlib,os,tempfile
from pathlib import Path
for row in PAYLOAD['files']:
    p=Path(row['path'])
    if not p.as_posix().startswith('/code/ai_onboarding/') or p.suffix!='.py': raise RuntimeError('Out-of-scope target')
    current=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
    if current!=row['expected']: raise RuntimeError('Live source changed since backup: '+str(p))
for row in PAYLOAD['files']:
    p=Path(row['path'])
    if row['content'] is None:
        p.unlink()
        continue
    raw=base64.b64decode(row['content'])
    fd,name=tempfile.mkstemp(prefix='.sico-step2-',suffix='.tmp',dir=p.parent)
    with os.fdopen(fd,'wb') as f: f.write(raw)
    os.chmod(name,row['mode'])
    os.replace(name,p)
    if p.read_bytes()!=raw: raise RuntimeError('Written bytes differ: '+str(p))
print(json.dumps({'files_written':len(PAYLOAD['files']),'paths':[r['path'] for r in PAYLOAD['files']]}))
'@ @{files=$payloadFiles}
}else{
    $result=Run-Frontend @'
const fs=require('fs'),crypto=require('crypto'),path=require('path');
const hash=p=>fs.existsSync(p)?crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'):null;
for(const row of PAYLOAD.files){if(!row.path.startsWith('/workspace/src/')||!(/\.(ts|svelte)$/.test(row.path)))throw Error('Out-of-scope target');if(hash(row.path)!==row.expected)throw Error('Live source changed since backup: '+row.path)}
PAYLOAD.files.sort((a,b)=>Number(a.path.includes('/routes/'))-Number(b.path.includes('/routes/')));
for(const row of PAYLOAD.files){if(row.content===null){fs.unlinkSync(row.path);continue}fs.mkdirSync(path.dirname(row.path),{recursive:true});const raw=Buffer.from(row.content,'base64'),tmp=row.path+'.sico-step2.tmp';fs.writeFileSync(tmp,raw,{mode:row.mode});fs.chmodSync(tmp,row.mode);fs.renameSync(tmp,row.path);if(!fs.readFileSync(row.path).equals(raw))throw Error('Written bytes differ: '+row.path)}
console.log(JSON.stringify({files_written:PAYLOAD.files.length,paths:PAYLOAD.files.map(r=>r.path),vite_hot_reload:true}));
'@ @{files=$payloadFiles}
}
[IO.File]::WriteAllText((Join-Path $snapshot ($Phase+'-result.json')),($result|ConvertTo-Json -Depth 6),$utf8)
$result|ConvertTo-Json -Depth 5
