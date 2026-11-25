[CmdletBinding()]
param(
    [string]$Repository = '',
    [string]$Version = ('agent-' + [DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss')),
    [string]$OutputRoot = (Join-Path $env:LOCALAPPDATA 'SICO_AI/agent-releases')
)
. (Join-Path $PSScriptRoot 'Common.ps1')
if (-not $Repository) { $Repository = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path }
if ($Version -notmatch '^agent-[0-9]{8}-[0-9]{6}$') { throw 'Unexpected version format' }
$release = Join-Path $OutputRoot $Version
if (Test-Path -LiteralPath $release) { throw 'Refusing to overwrite an existing release directory' }
New-Item -ItemType Directory -Path $release | Out-Null
foreach ($dir in @('scripts','backend-context/payload/ai_onboarding','backend-context/payload/ciso_assistant',
                  'frontend-source','frontend-context','validation','backup')) {
    New-Item -ItemType Directory -Path (Join-Path $release $dir) -Force | Out-Null
}
Get-ChildItem -LiteralPath $PSScriptRoot -File | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $release 'scripts')
}
$backend = Read-Container 'amro-backend'; Assert-Target $backend 'backend'
$frontend = Read-Container 'amro-frontend'; Assert-Target $frontend 'frontend'
$postgres = Read-Container 'amro-postgres'; Assert-Target $postgres 'postgres'
$caddy = Read-Container 'amro-caddy'; Assert-Target $caddy 'caddy'
$head = (& git -C $Repository rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Git inspection failed' }
$frontImages = Invoke-Docker @('image','inspect',$frontend.Image) | ConvertFrom-Json
$frontImage = @($frontImages)[0]
if ($frontImage.Config.Labels.'org.opencontainers.image.revision' -ne $head) {
    throw 'Current frontend image does not match HEAD; source baseline must be reviewed'
}
$composeFiles = @($backend.Config.Labels.'com.docker.compose.project.config_files' -split ',' | ForEach-Object {
    $path = [IO.Path]::GetFullPath($_)
    [pscustomobject]@{ path=$path; sha256=(File-Sha $path) }
})
$frontRollback = "sico-amro-frontend:rollback-$Version"
$backRollback = "sico-amro-backend:rollback-$Version"
Invoke-Docker @('image','tag',$backend.Image,$backRollback) | Out-Null
Invoke-Docker @('image','tag',$frontend.Image,$frontRollback) | Out-Null
Assert-Image $backRollback $backend.Image; Assert-Image $frontRollback $frontend.Image
$state = [pscustomobject]@{
    version=$Version; preparedUtc=[DateTime]::UtcNow.ToString('o'); repository=$Repository; gitHead=$head
    composeProject='grc_amro_test'; composeFiles=$composeFiles; runningContainers=@(Snapshot-Containers)
    previous=[pscustomobject]@{
        backend=[pscustomobject]@{ reference=$backend.Config.Image; id=$backend.Image; rollbackReference=$backRollback; entrypoint=$backend.Config.Entrypoint; command=$backend.Config.Cmd }
        frontend=[pscustomobject]@{ reference=$frontend.Config.Image; id=$frontend.Image; rollbackReference=$frontRollback; entrypoint=$frontend.Config.Entrypoint; command=$frontend.Config.Cmd }
    }
    release=[pscustomobject]@{
        backend=[pscustomobject]@{ reference="sico-amro-backend:$Version"; id='' }
        frontend=[pscustomobject]@{ reference="ghcr.io/sanaddiab6-del/grc_sc:sico-ai-next-$Version"; id='' }
    }
    status='prepared_not_built'
}
Write-Json (Join-Path $release 'state.json') $state

$toolsMount = "type=bind,source=$PSScriptRoot,target=/release-tools,readonly"
$inventory = Invoke-Docker @('run','--rm','--network','none','--entrypoint','/code/.venv/bin/python',
    '--mount',$toolsMount,$backend.Image,'/release-tools/image_inventory.py') | ConvertFrom-Json
Write-Json (Join-Path $release 'backend-base-inventory.json') $inventory
$backendFiles = @(
    'sico_ai_agent.py','sico_ai_agent_tools.py','sico_ai_agent_views.py','llm_provider.py','urls.py',
    'sico_ai_tool_hub_views.py','sico_ai_router_views.py','sico_ai_plan_views.py',
    'engagement_approval_views.py','engagement_service.py','engagement_views.py'
)
$sourceManifest = @()
foreach ($name in $backendFiles) {
    $relative = "ai_onboarding/$name"; $source = Join-Path $Repository "backend/$relative"
    $hash = File-Sha $source; $old = $inventory.PSObject.Properties[$relative]
    $normalizedHash = Text-Sha $source
    $changed = -not $old -or $old.Value -ne $normalizedHash
    if ($changed) { Copy-Item -LiteralPath $source -Destination (Join-Path $release "backend-context/payload/$relative") }
    $sourceManifest += [pscustomobject]@{ source="backend/$relative"; sha256=$hash; normalizedSha256=$normalizedHash; overlaid=[bool]$changed;
        baseSha256=$(if ($old) { $old.Value } else { $null }) }
}
# The engine introduces no model/migration delta relative to the deployed backend.
foreach ($path in @('ai_onboarding/models.py','core/models.py','iam/models.py') + @($inventory.PSObject.Properties.Name | Where-Object { $_ -like 'ai_onboarding/migrations/*' })) {
    $source = Join-Path $Repository "backend/$path"
    if ((Text-Sha $source) -ne $inventory.PSObject.Properties[$path].Value) { throw "Schema baseline drift: $path" }
}
foreach ($item in @(@('sico-agent-start.sh','payload/sico-agent-start.sh'),
                   @('sico_agent_release_settings.py','payload/ciso_assistant/sico_agent_release_settings.py'))) {
    $content = [IO.File]::ReadAllText((Join-Path $PSScriptRoot $item[0])).Replace("`r`n","`n")
    [IO.File]::WriteAllText((Join-Path $release "backend-context/$($item[1])"),$content,[Text.UTF8Encoding]::new($false))
}
$backendDockerfile = @"
ARG BASE_IMAGE
FROM `${BASE_IMAGE}
COPY payload/ /code/
RUN chmod 0555 /code/sico-agent-start.sh
ENV DJANGO_SETTINGS_MODULE=ciso_assistant.sico_agent_release_settings
ENTRYPOINT ["/code/sico-agent-start.sh"]
CMD []
LABEL sico.agent.release="$Version" sico.agent.base-image-id="$($backend.Image)"
"@
[IO.File]::WriteAllText((Join-Path $release 'backend-context/Dockerfile'),$backendDockerfile,[Text.UTF8Encoding]::new($false))

$archive = Join-Path $release 'frontend-head.tar'
& git -C $Repository archive --format=tar --output=$archive HEAD frontend
if ($LASTEXITCODE -ne 0) { throw 'Git archive failed' }
& tar -xf $archive -C (Join-Path $release 'frontend-source')
if ($LASTEXITCODE -ne 0) { throw 'Source extraction failed' }
foreach ($relative in @('frontend/src/routes/(app)/(internal)/sico-ai-next/+page.server.ts',
                         'frontend/src/routes/(app)/(internal)/sico-ai-next/+page.svelte')) {
    $source = Join-Path $Repository $relative
    Copy-Item -LiteralPath $source -Destination (Join-Path $release "frontend-source/$relative")
    $sourceManifest += [pscustomobject]@{ source=$relative; sha256=(File-Sha $source); overlaid=$true; baseSha256=$null }
}
# Reuse only the existing compiler plugin cache, never host node_modules or build output.
$cache = Join-Path $Repository 'frontend/project.inlang/cache'
if (Test-Path -LiteralPath $cache) {
    Copy-Item -LiteralPath $cache -Destination (Join-Path $release 'frontend-source/frontend/project.inlang/cache') -Recurse
}
Write-Json (Join-Path $release 'source-manifest.json') $sourceManifest
Write-Json (Join-Path $release 'source-status.json') ([pscustomobject]@{
    gitHead=$head; status=@(& git -C $Repository status --porcelain)
})
$releaseOverride = @{ services=@{
    backend=@{ image=$state.release.backend.reference; entrypoint=@('/code/sico-agent-start.sh'); command=@();
        environment=@{ DJANGO_SETTINGS_MODULE='ciso_assistant.sico_agent_release_settings';
                       SICO_ENGAGEMENT_COMMITS_ENABLED='false'; FORCE_CREATE_ADMIN='false' } }
    frontend=@{ image=$state.release.frontend.reference }
} }
Write-Json (Join-Path $release 'release.override.yml') $releaseOverride
$rollback = @{ services=@{
    backend=@{ image=$backRollback; entrypoint=@($backend.Config.Entrypoint); command=@($backend.Config.Cmd | ForEach-Object { $_.Replace('$','$$') }) }
    frontend=@{ image=$frontRollback; entrypoint=@($frontend.Config.Entrypoint); command=@($frontend.Config.Cmd | ForEach-Object { $_.Replace('$','$$') }) }
} }
Write-Json (Join-Path $release 'rollback.override.yml') $rollback
$changes = @(Assert-ReleaseConfig $state $release)
Write-Json (Join-Path $release 'compose-change-paths.json') $changes
Assert-ProtectedContainers $state
& (Join-Path $PSScriptRoot 'Refresh-BackendContext.ps1') -ReleaseDirectory $release
Write-Output "Prepared: $release"
Write-Output "Backend: $($state.release.backend.reference)"
Write-Output "Frontend: $($state.release.frontend.reference)"
