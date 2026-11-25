[CmdletBinding()]
param([Parameter(Mandatory)][string]$ReleaseDirectory)
. (Join-Path $PSScriptRoot 'Common.ps1')
$state = Read-Json (Join-Path $ReleaseDirectory 'state.json')
$pg = Read-Container 'amro-postgres'; Assert-Target $pg 'postgres'
$name = "sico-agent-pg-guard-$($state.version)"; $created=$false
try {
    Invoke-Docker @('run','--detach','--name',$name,'--label',"sico.agent.scratch=$($state.version)",
        '--network','none','--memory','384m','--tmpfs','/var/lib/postgresql/data:rw',
        '--env','PGDATA=/tmp/agent-release-pgdata','--env','POSTGRES_HOST_AUTH_METHOD=trust',
        '--env','POSTGRES_USER=agent_release','--env','POSTGRES_DB=agent_release_fixture',
        '--mount',"type=bind,source=$PSScriptRoot,target=/release-tools,readonly",$pg.Image) | Out-Null
    $created=$true; $ready=$false
    for ($i=0; $i -lt 60; $i++) {
        & docker exec $name pg_isready -U agent_release -d agent_release_fixture 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { $ready=$true; break }; Start-Sleep -Seconds 1
    }
    if (-not $ready) { throw 'PostgreSQL guard fixture did not become ready' }
    Invoke-Docker @('exec',$name,'psql','--set','ON_ERROR_STOP=1','-U','agent_release','-d','agent_release_fixture',
        '--file=/release-tools/pg_guard_fixture.sql') | Out-Null
    $result = Invoke-Docker @('run','--rm','--network',"container:$name",'--memory','512m',
        '--env','PYTHONPATH=/code','--env','HUEY_FILE_PATH=/tmp/pg-guard-huey.db',
        '--env','POSTGRES_NAME=agent_release_fixture','--env','POSTGRES_USER=agent_release',
        '--env','POSTGRES_PASSWORD=unused','--env','DB_HOST=127.0.0.1','--env','DB_PORT=5432',
        '--mount',"type=bind,source=$PSScriptRoot,target=/release-tools,readonly",'--entrypoint','/code/.venv/bin/python',
        $state.release.backend.reference,'/release-tools/verify_postgres_guard.py')
    [IO.File]::WriteAllLines((Join-Path $ReleaseDirectory 'validation/postgres-guard.json'),[string[]]$result,[Text.UTF8Encoding]::new($false))
} finally { if ($created) { Remove-OwnedScratch $name $state.version } }
Assert-ProtectedContainers $state
