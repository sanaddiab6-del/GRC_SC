[CmdletBinding()]
param([Parameter(Mandatory)][string]$ReleaseDirectory, [switch]$Execute)
. (Join-Path $PSScriptRoot 'Common.ps1')
$state = Read-Json (Join-Path $ReleaseDirectory 'state.json')
if ($Execute) {
    $seal = Read-Json (Join-Path $ReleaseDirectory 'seal.json')
    foreach ($file in $seal.files) {
        if ((File-Sha (Join-Path $ReleaseDirectory $file.path)) -ne $file.sha256) { throw "Sealed artifact changed: $($file.path)" }
    }
}
Assert-ProtectedContainers $state -AllowAppReplacement
Assert-Image $state.previous.backend.rollbackReference $state.previous.backend.id
Assert-Image $state.previous.frontend.rollbackReference $state.previous.frontend.id
foreach ($kind in @('backend','frontend')) {
    $current = Read-Container "amro-$kind"; Assert-Target $current $kind
    if ($current.Image -notin @($state.previous.$kind.id,$state.release.$kind.id)) { throw "Unrecognized $kind image; refusing rollback" }
}
$argsList = @(Compose-Args $state (Join-Path $ReleaseDirectory 'rollback.override.yml'))
$effective = Invoke-Docker ($argsList + @('config','--format','json')) | ConvertFrom-Json
$backendCommand = @($effective.services.backend.command | ForEach-Object { $_.Replace('$$','$') })
$frontendCommand = @($effective.services.frontend.command | ForEach-Object { $_.Replace('$$','$') })
if ($effective.services.backend.image -ne $state.previous.backend.rollbackReference -or
    $effective.services.frontend.image -ne $state.previous.frontend.rollbackReference -or
    (($effective.services.backend.entrypoint | ConvertTo-Json -Compress) -ne ($state.previous.backend.entrypoint | ConvertTo-Json -Compress)) -or
    (($frontendCommand | ConvertTo-Json -Compress) -ne ($state.previous.frontend.command | ConvertTo-Json -Compress)) -or
    (($backendCommand | ConvertTo-Json -Compress) -ne ($state.previous.backend.command | ConvertTo-Json -Compress))) {
    throw 'Rollback does not reproduce the previous image/startup configuration'
}
$argsList += @('up','-d','--no-deps','--no-build','--pull','never','--force-recreate','backend','frontend')
Write-Output ('Prepared rollback: docker ' + (($argsList | ForEach-Object { Quote-WindowsArgument $_ }) -join ' '))
if (-not $Execute) { Write-Output 'DRY RUN: no services changed and no database restore attempted.'; return }
Invoke-Docker $argsList
foreach ($kind in @('backend','frontend')) {
    if ((Read-Container "amro-$kind").Image -ne $state.previous.$kind.id) { throw "Rollback image mismatch for $kind" }
}
Assert-ProtectedContainers $state -AllowAppReplacement
Write-Output 'Previous application images restored. No database restore or migration was performed.'
