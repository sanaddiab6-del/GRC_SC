[CmdletBinding()]
param([Parameter(Mandatory)][string]$ReleaseDirectory)
. (Join-Path $PSScriptRoot 'Common.ps1')
$state = Read-Json (Join-Path $ReleaseDirectory 'state.json')
Assert-ProtectedContainers $state
$pg = Read-Container 'amro-postgres'; Assert-Target $pg 'postgres'
$envMap = Read-Environment $pg
$dbUser = $envMap['POSTGRES_USER']; $dbName = $envMap['POSTGRES_DB']
if (-not $dbUser -or -not $dbName) { throw 'Cannot establish the existing test database identity' }
$folder = Join-Path $ReleaseDirectory ('backup/' + [DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss'))
if (Test-Path -LiteralPath $folder) { throw 'Backup destination already exists' }
New-Item -ItemType Directory -Path $folder | Out-Null
$dump = Join-Path $folder 'sico-test.dump'
$capturedUtc = [DateTime]::UtcNow.ToString('o')
Export-DockerBinary @('exec','amro-postgres','pg_dump','--format=custom','--no-owner','--no-acl',
    '--lock-wait-timeout=5000',"--username=$dbUser","--dbname=$dbName") $dump
$header = [IO.File]::OpenRead($dump)
try { $bytes = New-Object byte[] 5; [void]$header.Read($bytes,0,5); if ([Text.Encoding]::ASCII.GetString($bytes) -ne 'PGDMP') { throw 'Invalid custom-format dump' } }
finally { $header.Dispose() }
$name = "sico-agent-restore-$($state.version)-$([DateTime]::UtcNow.ToString('HHmmss'))"
$created = $false
try {
    Invoke-Docker @('run','--detach','--name',$name,'--label',"sico.agent.scratch=$($state.version)",
        '--network','none','--memory','768m','--tmpfs','/var/lib/postgresql/data:rw',
        '--mount',"type=bind,source=$PSScriptRoot,target=/release-tools,readonly",
        '--env','PGDATA=/tmp/sico-agent-postgres-data','--env','POSTGRES_HOST_AUTH_METHOD=trust',
        '--env',"POSTGRES_USER=$dbUser",'--env',"POSTGRES_DB=$dbName",$pg.Image) | Out-Null
    $created = $true; $ready = $false
    for ($i=0; $i -lt 90; $i++) {
        & docker exec $name pg_isready "--username=$dbUser" "--dbname=$dbName" 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { $ready=$true; break }; Start-Sleep -Seconds 1
    }
    if (-not $ready) { throw 'Disposable restore PostgreSQL did not become ready' }
    $scratch = Read-Container $name
    if ($scratch.HostConfig.NetworkMode -ne 'none' -or @($scratch.Mounts | Where-Object Type -eq 'volume').Count) { throw 'Unsafe restore sandbox' }
    Invoke-Docker @('cp',$dump,"${name}:/tmp/sico-test.dump") | Out-Null
    $toc = Invoke-Docker @('exec',$name,'pg_restore','--list','/tmp/sico-test.dump')
    [IO.File]::WriteAllLines((Join-Path $folder 'archive-contents.txt'),[string[]]$toc,[Text.UTF8Encoding]::new($false))
    Invoke-Docker @('exec',$name,'pg_restore','--exit-on-error','--single-transaction','--no-owner','--no-acl',
        "--username=$dbUser","--dbname=$dbName",'/tmp/sico-test.dump') | Out-Null
    $rows = Invoke-Docker @('exec',$name,'psql','--tuples-only','--no-align','--quiet','--set','ON_ERROR_STOP=1',
        "--username=$dbUser","--dbname=$dbName",'--file=/release-tools/restore_checks.sql')
    $counts = ($rows | Where-Object { $_ -match '^\{' }) | ConvertFrom-Json
    if (-not $counts -or $counts.public_tables -lt 20) { throw 'Restored database sanity check failed' }
    $manifest = [pscustomobject]@{
        verified=$true; capturedUtc=$capturedUtc; restoreVerifiedUtc=[DateTime]::UtcNow.ToString('o'); sourceContainerId=$pg.Id;
        sourceImageId=$pg.Image; sourceProject='grc_amro_test'; sourceDatabase=$dbName;
        file=$dump; sha256=(File-Sha $dump); bytes=(Get-Item -LiteralPath $dump).Length;
        restoreMode='new disposable network-none PostgreSQL with container-private PGDATA, no Docker volumes';
        restoreExitCode=0; restoredCounts=$counts; originalDatabaseModified=$false
    }
    $manifestPath = Join-Path $folder 'verified.json'; Write-Json $manifestPath $manifest
    Write-Json (Join-Path $ReleaseDirectory 'backup/latest-verified.json') ([pscustomobject]@{
        manifestPath=$manifestPath; sha256=(File-Sha $manifestPath)
    })
    Write-Output "Backup and disposable restore verified: $dump"
    Write-Output ($counts | ConvertTo-Json -Compress)
} finally { if ($created) { Remove-OwnedScratch $name $state.version } }
Assert-ProtectedContainers $state
