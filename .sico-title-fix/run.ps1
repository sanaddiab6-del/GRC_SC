param([ValidateSet('unit','activate','reload','rollback','real')][string]$Mode='unit')
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$snapshot=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'current.txt'))
$files=@('backend/ai_onboarding/quality_sico_drafts_v5.py','backend/ai_onboarding/llm_provider.py')
$payload=@{}
if($Mode -eq 'unit'){
    $sources=@{}
    foreach($file in ($files+@('backend/ai_onboarding/tests/test_quality_title_recovery.py','backend/ai_onboarding/tests/test_quality_evidence_requests.py'))){$sources[$file]=[Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $root $file)))}
    $bootstrap=[IO.File]::ReadAllText((Join-Path $root '.sico-reconcile/validate_backend.py'))
    $payload=@{sources=$sources;bootstrap=$bootstrap.Substring(0,$bootstrap.IndexOf('attempts ='))}
}
if($Mode -in 'activate','rollback'){
    $entries=@()
    foreach($file in $files){
        $name=Split-Path $file -Leaf
        $before=Join-Path $snapshot $name
        $source=if($Mode -eq 'rollback'){$before}else{Join-Path $root $file}
        $expected=if($Mode -eq 'rollback'){$target=Join-Path $root $file;(Get-FileHash -LiteralPath $target).Hash.ToLower()}else{(Get-FileHash -LiteralPath $before).Hash.ToLower()}
        $entries+=@{path='/code/ai_onboarding/'+$name;expected=$expected;content=[Convert]::ToBase64String([IO.File]::ReadAllBytes($source));backup=$before}
    }
    $payload=@{files=$entries}
}
if($Mode -eq 'real'){
    $evidence=ConvertFrom-Json -InputObject ([IO.File]::ReadAllText((Join-Path $root '.sico-step2/qwen-evidence.json')))
    $payload=@{organization=$evidence.Organization;framework=$evidence.Framework.name;
        objective='Prepare an assessment charter for a proposed regional delivery operator handling customer addresses, dispatcher access and supplier integrations. Identify scope boundaries, responsible roles and evidence needed to verify the selected installed framework edition. All organization details require verification.'}
}
$encoded=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($payload|ConvertTo-Json -Depth 9 -Compress)))
$script="import json,base64`nPAYLOAD=json.loads(base64.b64decode('$encoded'))`n"
if($Mode -in 'unit','real'){
    $script+=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'check.py'))
    $script=$script.Replace("MODE = None",("MODE = '"+$Mode+"'"))
}elseif($Mode -eq 'reload'){
    $script+=@'
import os,signal
from pathlib import Path
if '/code/.venv/bin/gunicorn' not in Path('/proc/1/cmdline').read_bytes().replace(b'\0',b' ').decode(): raise RuntimeError('Unexpected master; stopped')
os.kill(1,signal.SIGHUP)
print(json.dumps({'workers_reloaded':True,'container_restarted':False}))
'@
}else{
    $script+=@'
import os,hashlib,tempfile
from pathlib import Path
for row in PAYLOAD['files']:
    p=Path(row['path'])
    if p.parent!=Path('/code/ai_onboarding') or p.name not in ('quality_sico_drafts_v5.py','llm_provider.py'): raise RuntimeError('Out of scope')
    if hashlib.sha256(p.read_bytes()).hexdigest()!=row['expected']: raise RuntimeError('Unresolved live difference: '+str(p))
results=[]
for row in PAYLOAD['files']:
    p=Path(row['path']);mode=p.stat().st_mode&0o777;raw=base64.b64decode(row['content'])
    fd,name=tempfile.mkstemp(prefix='.title-fix-',suffix='.tmp',dir=p.parent)
    with os.fdopen(fd,'wb') as f: f.write(raw)
    os.chmod(name,mode);os.replace(name,p)
    assert p.read_bytes()==raw
    results.append({'path':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'backup':row['backup']})
print(json.dumps(results))
'@
}
$raw=$script|docker exec -i -e PYTHONDONTWRITEBYTECODE=1 amro-backend /code/.venv/bin/python -B -u -
$code=$LASTEXITCODE
$utf8=New-Object Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $PSScriptRoot ($Mode+'-result.json')),($raw -join "`n"),$utf8)
Write-Output ($raw -join "`n")
if($code -ne 0){throw "$Mode failed ($code)"}
