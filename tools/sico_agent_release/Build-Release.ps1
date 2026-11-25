[CmdletBinding()]
param([Parameter(Mandatory)][string]$ReleaseDirectory, [switch]$Resume,
      [ValidateRange(1024,16384)][int]$MemoryMiB=3400,
      [ValidateRange(512,12288)][int]$NodeHeapMiB=2560, [switch]$LowMemoryFrontend)
. (Join-Path $PSScriptRoot 'Common.ps1')
$statePath = Join-Path $ReleaseDirectory 'state.json'; $state = Read-Json $statePath
Assert-ProtectedContainers $state
if ($state.status -ne 'prepared_not_built' -and -not ($Resume -and $state.status -eq 'backend_built_frontend_pending')) { throw 'Build requires a prepared release or explicit resume of its frontend build' }
Assert-Image $state.previous.backend.rollbackReference $state.previous.backend.id
Assert-Image $state.previous.frontend.rollbackReference $state.previous.frontend.id
foreach ($entry in (Read-Json (Join-Path $ReleaseDirectory 'source-manifest.json'))) {
    if ((File-Sha (Join-Path $state.repository $entry.source)) -ne $entry.sha256) { throw "Source drift: $($entry.source)" }
}
$backContext = Join-Path $ReleaseDirectory 'backend-context'
if ($state.status -eq 'prepared_not_built') {
    Invoke-Docker @('build','--pull=false','--network=none','--build-arg',"BASE_IMAGE=$($state.previous.backend.rollbackReference)",
        '--tag',$state.release.backend.reference,$backContext)
} else { Assert-Image $state.release.backend.reference $state.release.backend.id }
$state.release.backend.id = (Invoke-Docker @('image','inspect',$state.release.backend.reference,'--format','{{.Id}}')).Trim()
$state.status = 'backend_built_frontend_pending'; Write-Json $statePath $state

$source = Join-Path $ReleaseDirectory 'frontend-source/frontend'
$depsMount = 'type=volume,source=sico_ai_next_preview_modules,target=/deps,readonly'
$nodeImage = (Invoke-Docker @('image','inspect','node:22-bookworm-slim','--format','{{.Id}}')).Trim()
$memoryInfo = Invoke-Docker @('run','--rm','--network','none','--memory','64m','--entrypoint','cat',$nodeImage,'/proc/meminfo')
$availableMiB = 0L
foreach ($line in $memoryInfo) { if ($line -match '^MemAvailable:\s+(\d+)\s+kB') { $availableMiB = [long]$Matches[1] / 1024 } }
if ($availableMiB -lt ($MemoryMiB + 512)) { throw "Insufficient isolated build headroom: $availableMiB MiB available; $($MemoryMiB + 512) MiB required. No build started." }
if ($NodeHeapMiB -gt ($MemoryMiB - 512)) { throw 'Node heap must leave at least 512 MiB for native allocations' }
$lockLine = Invoke-Docker @('run','--rm','--network','none','--entrypoint','sha256sum','--mount',$depsMount,$nodeImage,'/deps/.pnpm/lock.yaml')
$dependencyLock = ($lockLine -split '\s+')[0]
if ($dependencyLock -ne (Text-Sha (Join-Path $source 'pnpm-lock.yaml'))) { throw 'Installed frontend dependency lock differs from the source lock' }
Write-Json (Join-Path $ReleaseDirectory 'frontend-build-dependencies.json') ([pscustomobject]@{
    nodeImageId=$nodeImage; dependencyVolume='sico_ai_next_preview_modules'; pnpmLockSha256=$dependencyLock;
    productionOnlyBuildAdjustment='Paraglide emitTsDeclarations=false in disposable build copy; runtime translations unchanged';
    nodeHeapMiB=$NodeHeapMiB; memoryLimitMiB=$MemoryMiB; cpus=2; minified=(-not [bool]$LowMemoryFrontend)
})
$name = "sico-agent-build-$($state.version)"
if (@(Invoke-Docker @('ps','-aq','--filter',"name=^/$name`$")).Count) { Remove-OwnedScratch $name $state.version }
$created = $false
try {
    Invoke-Docker @('run','--detach','--name',$name,'--label',"sico.agent.scratch=$($state.version)",
        '--network','none','--memory',"${MemoryMiB}m",'--memory-swap',"${MemoryMiB}m",'--cpus','2',
        '--env',"NODE_OPTIONS=--max-old-space-size=$NodeHeapMiB --max-semi-space-size=16",
        '--env',"SICO_LOW_MEMORY_BUILD=$(([bool]$LowMemoryFrontend).ToString().ToLowerInvariant())",
        '--mount',"type=bind,source=$source,target=/source,readonly",'--mount','type=volume,source=sico_ai_next_preview_modules,target=/tmp/frontend/node_modules,readonly',
        '--mount',"type=bind,source=$PSScriptRoot,target=/release-tools,readonly",
        '--entrypoint','/bin/sh',$nodeImage,'/release-tools/frontend-build.sh') | Out-Null
    $created = $true; $watch = [Diagnostics.Stopwatch]::StartNew()
    while ((Read-Container $name).State.Running) {
        if ($watch.Elapsed.TotalMinutes -gt 25) { throw 'Frontend build exceeded its isolated build budget' }
        Start-Sleep -Seconds 3
    }
    $result = Read-Container $name
    Write-Json (Join-Path $ReleaseDirectory 'validation/frontend-build-state.json') ([pscustomobject]@{
        exitCode=$result.State.ExitCode; oomKilled=$result.State.OOMKilled; memoryLimitBytes=$result.HostConfig.Memory
    })
    $logs = Read-DockerLogs $name
    [IO.File]::WriteAllLines((Join-Path $ReleaseDirectory 'validation/frontend-build.log'),[string[]]$logs,[Text.UTF8Encoding]::new($false))
    if ($result.State.ExitCode -ne 0) { throw "Frontend build failed with exit $($result.State.ExitCode). See validation/frontend-build.log" }
    $context = Join-Path $ReleaseDirectory 'frontend-context'
    Invoke-Docker @('cp',"${name}:/tmp/frontend/build",(Join-Path $context 'build')) | Out-Null
    $dockerfile = @"
ARG BASE_IMAGE
FROM `${BASE_IMAGE}
RUN rm -rf /app/build
COPY build/ /app/build/
LABEL sico.agent.release="$($state.version)" sico.agent.base-image-id="$($state.previous.frontend.id)" sico.agent.frontend.minified="$((-not [bool]$LowMemoryFrontend).ToString().ToLowerInvariant())"
"@
    [IO.File]::WriteAllText((Join-Path $context 'Dockerfile'),$dockerfile,[Text.UTF8Encoding]::new($false))
    Invoke-Docker @('build','--pull=false','--network=none','--build-arg',"BASE_IMAGE=$($state.previous.frontend.rollbackReference)",
        '--tag',$state.release.frontend.reference,$context)
    $state.release.frontend.id = (Invoke-Docker @('image','inspect',$state.release.frontend.reference,'--format','{{.Id}}')).Trim()
    $state.status = 'built_not_validated'; Write-Json $statePath $state
} finally {
    if ($created) { Remove-OwnedScratch $name $state.version }
}
Assert-ProtectedContainers $state
Write-Output "Built backend: $($state.release.backend.reference)"
Write-Output "Built frontend: $($state.release.frontend.reference)"
