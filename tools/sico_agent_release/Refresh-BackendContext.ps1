[CmdletBinding()]
param([Parameter(Mandatory)][string]$ReleaseDirectory, [switch]$Rebuild)
. (Join-Path $PSScriptRoot 'Common.ps1')
$statePath = Join-Path $ReleaseDirectory 'state.json'; $state = Read-Json $statePath
if (Test-Path -LiteralPath (Join-Path $ReleaseDirectory 'seal.json')) { throw 'A sealed release cannot be refreshed' }
Assert-ProtectedContainers $state
Assert-Image $state.previous.backend.rollbackReference $state.previous.backend.id
$raw = Invoke-Docker @('run','--rm','--network','none','--mount',
    "type=bind,source=$(Join-Path $state.repository 'backend'),target=/source-backend,readonly",'--mount',
    "type=bind,source=$PSScriptRoot,target=/release-tools,readonly",'--entrypoint','/code/.venv/bin/python',
    $state.previous.backend.rollbackReference,'/release-tools/dependency_inventory.py')
$entries = $raw | ConvertFrom-Json
$old = @(Read-Json (Join-Path $ReleaseDirectory 'source-manifest.json'))
foreach ($entry in $old) {
    if ((File-Sha (Join-Path $state.repository $entry.source)) -ne $entry.sha256) { throw "Source changed during preparation: $($entry.source)" }
}
foreach ($entry in $entries) {
    if ($entry.overlaid) {
        if ($entry.relative -eq 'ai_onboarding/models.py' -or $entry.relative -like '*/migrations/*') { throw 'Schema source cannot be overlaid' }
        $destination = Join-Path $ReleaseDirectory "backend-context/payload/$($entry.relative)"
        New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force | Out-Null
        Copy-Item -LiteralPath (Join-Path $state.repository $entry.source) -Destination $destination
    }
}
Write-Json (Join-Path $ReleaseDirectory 'source-manifest.json') (@($entries) + @($old | Where-Object source -like 'frontend/*'))
Write-Json (Join-Path $ReleaseDirectory 'backend-import-closure.json') $entries
if ($Rebuild) {
    if ($state.status -notin @('built_not_validated','backend_built_frontend_pending')) { throw 'Unexpected backend rebuild state' }
    $active = @(Invoke-Docker @('ps','-q','--filter',"name=^/sico-agent-build-$($state.version)`$"))
    if ($active.Count) { throw 'Wait until the frontend builder has stopped before recording a backend rebuild' }
    Invoke-Docker @('build','--pull=false','--network=none','--build-arg',"BASE_IMAGE=$($state.previous.backend.rollbackReference)",
        '--tag',$state.release.backend.reference,(Join-Path $ReleaseDirectory 'backend-context'))
    $state.release.backend.id = (Invoke-Docker @('image','inspect',$state.release.backend.reference,'--format','{{.Id}}')).Trim()
    Write-Json $statePath $state
}
Write-Output 'Backend import closure captured; no running service changed.'
