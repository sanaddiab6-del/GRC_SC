[CmdletBinding()]
param([Parameter(Mandatory)][string]$ReleaseDirectory)
. (Join-Path $PSScriptRoot 'Common.ps1')
$state = Read-Json (Join-Path $ReleaseDirectory 'state.json')
Assert-ProtectedContainers $state
Assert-Image $state.release.backend.reference $state.release.backend.id
Assert-Image $state.previous.backend.rollbackReference $state.previous.backend.id
Assert-Image $state.previous.frontend.rollbackReference $state.previous.frontend.id
foreach ($entry in (Read-Json (Join-Path $ReleaseDirectory 'source-manifest.json'))) {
    if ((File-Sha (Join-Path $state.repository $entry.source)) -ne $entry.sha256) { throw "Source changed: $($entry.source)" }
}
$backend = Read-Json (Join-Path $ReleaseDirectory 'validation/backend-results.json')
$guard = Read-Json (Join-Path $ReleaseDirectory 'validation/postgres-guard.json')
$pointer = Read-Json (Join-Path $ReleaseDirectory 'backup/latest-verified.json')
if ((File-Sha $pointer.manifestPath) -ne $pointer.sha256) { throw 'Backup evidence changed' }
$backup = Read-Json $pointer.manifestPath
if (-not $backup.verified -or (File-Sha $backup.file) -ne $backup.sha256) { throw 'Backup checksum failed' }
$images = Read-Json (Join-Path $ReleaseDirectory 'previous-images.json')
if ((File-Sha $images.archive) -ne $images.sha256) { throw 'Rollback archive checksum failed' }
$frontendBuilt = [bool]$state.release.frontend.id
if ($frontendBuilt) { Assert-Image $state.release.frontend.reference $state.release.frontend.id }
$build = Read-Json (Join-Path $ReleaseDirectory 'validation/frontend-build-state.json')
$memoryInfo = Invoke-Docker @('run','--rm','--network','none','--memory','64m','--entrypoint','cat','node:22-bookworm-slim','/proc/meminfo')
$availableMiB=0L
foreach ($line in $memoryInfo) { if ($line -match '^MemAvailable:\s+(\d+)\s+kB') { $availableMiB=[long]$Matches[1]/1024 } }
$os = Get-CimInstance Win32_OperatingSystem
$result = [pscustomobject]@{
    version=$state.version; recordedUtc=[DateTime]::UtcNow.ToString('o');
    readyForDeployment=($state.status -eq 'validated_not_deployed' -and $frontendBuilt);
    backendImage=$state.release.backend; backendValidated=$backend.passed;
    frontendImage=$state.release.frontend; frontendBuilt=$frontendBuilt;
    frontendBuildExitCode=$build.exitCode; frontendOOMKilled=$build.oomKilled;
    frontendBuildMemoryLimitBytes=$build.memoryLimitBytes;
    dockerAvailableMemoryMiB=$availableMiB; hostFreePhysicalGiB=[math]::Round($os.FreePhysicalMemory/1MB,2);
    postgresqlReadOnlyVerified=$guard.write_rejected_by_postgresql;
    backupVerified=$backup.verified; backupFile=$backup.file; backupSha256=$backup.sha256;
    previousImagesArchived=$true; previousImagesArchive=$images.archive;
    sourceFilesUnchanged=$true; acceptedContainerBaselineUnchanged=$true;
    externalDockerRestartConfirmedAndAudited=(@(Get-ChildItem -LiteralPath $ReleaseDirectory -Filter 'confirmed-external-restart-*.json' -File).Count -gt 0);
    deploymentExecuted=(Test-Path -LiteralPath (Join-Path $ReleaseDirectory 'deployment-receipt.json'));
    blocker=$(if (-not $frontendBuilt) { 'Frontend full build exceeded available memory, including the low-memory candidate. No frontend release image exists; deployment remains blocked.' } else { '' })
}
Write-Json (Join-Path $ReleaseDirectory 'readiness.json') $result
Write-Output ($result | ConvertTo-Json -Depth 8)
