[CmdletBinding()]
param([Parameter(Mandatory)][string]$ReleaseDirectory, [Parameter(Mandatory)][switch]$ExternalRestartConfirmed)
. (Join-Path $PSScriptRoot 'Common.ps1')
if (-not $ExternalRestartConfirmed) { throw 'External restart confirmation is required' }
$path = Join-Path $ReleaseDirectory 'state.json'; $state = Read-Json $path
if (Test-Path -LiteralPath (Join-Path $ReleaseDirectory 'seal.json')) { throw 'A sealed release requires a separate review' }
$current = @(Snapshot-Containers)
foreach ($prior in $state.runningContainers) {
    $now = @($current | Where-Object name -eq $prior.name)
    if ($now.Count -ne 1 -or $now[0].id -ne $prior.id -or $now[0].image -ne $prior.image) {
        throw "Changes exceed an external restart: $($prior.name)"
    }
}
Compose-Args $state '' | Out-Null
$stamp = [DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss')
Copy-Item -LiteralPath $path -Destination (Join-Path $ReleaseDirectory "state.before-confirmed-restart-$stamp.json")
Write-Json (Join-Path $ReleaseDirectory "confirmed-external-restart-$stamp.json") ([pscustomobject]@{
    confirmedUtc=[DateTime]::UtcNow.ToString('o'); reason='User explicitly confirmed Docker was restarted externally';
    prior=$state.runningContainers; current=$current; containerAndImageIdsUnchanged=$true;
    agentIssuedRestart=$false
})
$state.runningContainers = $current
Write-Json $path $state
Assert-ProtectedContainers $state
Write-Output 'Confirmed external restart recorded; only start-time baseline refreshed. Original baseline preserved.'
