[CmdletBinding()]
param([Parameter(Mandatory)][string]$ReleaseDirectory, [switch]$Execute)
. (Join-Path $PSScriptRoot 'Common.ps1')
$state = Read-Json (Join-Path $ReleaseDirectory 'state.json')
if (-not $Execute) {
    Assert-ProtectedContainers $state
    Assert-ReleaseConfig $state $ReleaseDirectory | Out-Null
    $plan = @(Compose-Args $state (Join-Path $ReleaseDirectory 'release.override.yml'))
    $plan += @('up','-d','--no-deps','--no-build','--pull','never','--force-recreate','backend','frontend')
    Write-Output ('Prepared command: docker ' + (($plan | ForEach-Object { Quote-WindowsArgument $_ }) -join ' '))
    Write-Output "DRY RUN: no services changed. Preparation status: $($state.status)."
    if ($state.status -ne 'validated_not_deployed' -or -not (Test-Path -LiteralPath (Join-Path $ReleaseDirectory 'seal.json'))) {
        Write-Output 'BLOCKED: the complete release is not validated/sealed; -Execute will refuse deployment.'
    }
    return
}
if ($state.status -ne 'validated_not_deployed') { throw 'Release is not validated. Deployment is blocked.' }
$seal = Read-Json (Join-Path $ReleaseDirectory 'seal.json')
foreach ($file in $seal.files) {
    if ((File-Sha (Join-Path $ReleaseDirectory $file.path)) -ne $file.sha256) { throw "Sealed artifact changed: $($file.path)" }
}
Assert-ProtectedContainers $state
Assert-Image $state.release.backend.reference $state.release.backend.id
Assert-Image $state.release.frontend.reference $state.release.frontend.id
Assert-Image $state.previous.backend.rollbackReference $state.previous.backend.id
Assert-Image $state.previous.frontend.rollbackReference $state.previous.frontend.id
Assert-ReleaseConfig $state $ReleaseDirectory | Out-Null
$pointer = Read-Json (Join-Path $ReleaseDirectory 'backup/latest-verified.json')
if ((File-Sha $pointer.manifestPath) -ne $pointer.sha256) { throw 'Backup manifest changed' }
$backup = Read-Json $pointer.manifestPath
if (-not $backup.verified -or (File-Sha $backup.file) -ne $backup.sha256) { throw 'Verified backup is unavailable' }
$argsList = @(Compose-Args $state (Join-Path $ReleaseDirectory 'release.override.yml'))
$argsList += @('up','-d','--no-deps','--no-build','--pull','never','--force-recreate','backend','frontend')
Write-Output ('Prepared command: docker ' + (($argsList | ForEach-Object { Quote-WindowsArgument $_ }) -join ' '))
if (-not $Execute) { Write-Output 'DRY RUN: no running service changed. Separate deployment approval is required.'; return }
if (([DateTime]::UtcNow - [DateTime]::Parse($backup.capturedUtc).ToUniversalTime()).TotalHours -gt 4) {
    throw 'Backup is older than four hours. Run Backup-Verify and Seal-Release again before deployment.'
}
# This is the only application-changing command. Literal service allowlist and --no-deps.
Invoke-Docker $argsList
for ($i=0; $i -lt 90; $i++) {
    $backend = Read-Container 'amro-backend'; $frontend = Read-Container 'amro-frontend'
    $healthy = $backend.State.Running -and $frontend.State.Running
    if ($backend.State.PSObject.Properties['Health']) { $healthy = $healthy -and $backend.State.Health.Status -eq 'healthy' }
    if ($healthy) { break }; Start-Sleep -Seconds 2
}
if (-not $healthy -or $backend.Image -ne $state.release.backend.id -or $frontend.Image -ne $state.release.frontend.id) {
    throw 'Release health/image verification failed. Use the prepared Rollback-Release script after reviewing the failure.'
}
Assert-ProtectedContainers $state -AllowAppReplacement
Write-Json (Join-Path $ReleaseDirectory 'deployment-receipt.json') ([pscustomobject]@{
    deployedUtc=[DateTime]::UtcNow.ToString('o'); backendContainerId=$backend.Id; frontendContainerId=$frontend.Id;
    backendImageId=$backend.Image; frontendImageId=$frontend.Image; onlyAppServicesChanged=$true
})
Write-Output 'Approved deployment completed. PostgreSQL, Caddy and other stacks were not recreated.'
