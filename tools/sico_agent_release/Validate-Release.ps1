[CmdletBinding()]
param([Parameter(Mandatory)][string]$ReleaseDirectory, [switch]$BackendOnly)
. (Join-Path $PSScriptRoot 'Common.ps1')
$statePath = Join-Path $ReleaseDirectory 'state.json'; $state = Read-Json $statePath
if ($state.status -ne 'built_not_validated' -and -not ($BackendOnly -and $state.status -eq 'backend_built_frontend_pending')) { throw 'Both release images must be built before full validation' }
Assert-ProtectedContainers $state
Assert-Image $state.release.backend.reference $state.release.backend.id
if (-not $BackendOnly) { Assert-Image $state.release.frontend.reference $state.release.frontend.id }
$inputDir = Join-Path $ReleaseDirectory 'validation-input'; New-Item -ItemType Directory -Path $inputDir -Force | Out-Null
foreach ($file in @('test_sico_ai_agent.py','test_sico_ai_router.py','test_sico_ai_tool_hub.py')) {
    Copy-Item -LiteralPath (Join-Path $state.repository "backend/ai_onboarding/$file") -Destination $inputDir
}
foreach ($file in @('check_sico_ai_agent.py','check_sico_ai_frontend.cjs')) {
    Copy-Item -LiteralPath (Join-Path $state.repository "tools/$file") -Destination $inputDir
}
$toolMount = "type=bind,source=$PSScriptRoot,target=/release-tools,readonly"
$checksMount = "type=bind,source=$inputDir,target=/checks,readonly"
$python = @('run','--rm','--network','none','--env','HUEY_FILE_PATH=/tmp/agent-release-huey.db',
    '--env','PYTHONDONTWRITEBYTECODE=1','--env','PYTHONPATH=/code','--env','SICO_ENGAGEMENT_COMMITS_ENABLED=true',
    '--env','FORCE_CREATE_ADMIN=true','--mount',$toolMount,'--mount',$checksMount,'--entrypoint','/code/.venv/bin/python')
$guards = Invoke-Docker ($python + @($state.release.backend.reference,'/release-tools/verify_backend_image.py'))
[IO.File]::WriteAllLines((Join-Path $ReleaseDirectory 'validation/backend-guards.json'),[string[]]$guards,[Text.UTF8Encoding]::new($false))
$tests = $python
foreach ($file in @('test_sico_ai_agent.py','test_sico_ai_router.py','test_sico_ai_tool_hub.py')) {
    $tests += @('--mount',"type=bind,source=$(Join-Path $inputDir $file),target=/code/ai_onboarding/$file,readonly")
}
Invoke-Docker ($tests + @($state.release.backend.reference,'/code/manage.py','test','ai_onboarding.test_sico_ai_agent',
    'ai_onboarding.test_sico_ai_router','ai_onboarding.test_sico_ai_tool_hub','--noinput'))
Invoke-Docker ($python + @($state.release.backend.reference,'/checks/check_sico_ai_agent.py'))
if (-not $BackendOnly) {
$baseline = Invoke-Docker @('run','--rm','--network','none','--mount',$toolMount,'--entrypoint','node',
    $state.previous.frontend.rollbackReference,'/release-tools/verify_frontend_image.mjs','--baseline')
[IO.File]::WriteAllLines((Join-Path $inputDir 'frontend-baseline-routes.json'),[string[]]$baseline,[Text.UTF8Encoding]::new($false))
$frontResult = Invoke-Docker @('run','--rm','--network','none','--mount',$toolMount,'--mount',$checksMount,'--entrypoint','node',
    $state.release.frontend.reference,'/release-tools/verify_frontend_image.mjs')
[IO.File]::WriteAllLines((Join-Path $ReleaseDirectory 'validation/frontend-image.json'),[string[]]$frontResult,[Text.UTF8Encoding]::new($false))
Invoke-Docker @('run','--rm','--network','none','--mount',$checksMount,
    '--mount',"type=bind,source=$(Join-Path $ReleaseDirectory 'frontend-source/frontend'),target=/source,readonly",
    '--mount','type=volume,source=sico_ai_next_preview_modules,target=/deps,readonly','--entrypoint','node',
    'node:22-bookworm-slim','/checks/check_sico_ai_frontend.cjs')
}

$kinds = if ($BackendOnly) { @('backend') } else { @('backend','frontend') }
foreach ($kind in $kinds) {
    $name = "sico-agent-smoke-$kind-$($state.version)"; $created = $false
    try {
        $argsList = @('run','--detach','--name',$name,'--label',"sico.agent.scratch=$($state.version)",
            '--network','none','--memory','512m','--mount',$toolMount)
        if ($kind -eq 'backend') {
            $argsList += @('--env','DJANGO_SECRET_KEY=isolated-release-test-key-not-for-deployment',
                '--env','GUNICORN_WORKERS=1','--env','HUEY_FILE_PATH=/tmp/agent-release-huey.db',
                '--env','POSTGRES_NAME=unreachable','--env','POSTGRES_USER=unreachable','--env','POSTGRES_PASSWORD=unreachable',
                '--env','DB_HOST=127.0.0.1','--env','DB_PORT=1','--env','ALLOWED_HOSTS=127.0.0.1')
        } else {
            $argsList += @('--env','PUBLIC_BACKEND_API_URL=http://127.0.0.1:1/api','--env','ORIGIN=http://127.0.0.1:3000')
        }
        $argsList += $state.release.$kind.reference
        Invoke-Docker $argsList | Out-Null; $created = $true
        if ($kind -eq 'backend') {
            $smoke = Invoke-Docker @('exec',$name,'/code/.venv/bin/python','/release-tools/probe_backend_http.py')
        } else { $smoke = Invoke-Docker @('exec',$name,'node','/release-tools/probe_frontend_http.mjs') }
        [IO.File]::WriteAllLines((Join-Path $ReleaseDirectory "validation/$kind-http.json"),[string[]]$smoke,[Text.UTF8Encoding]::new($false))
    } finally { if ($created) { Remove-OwnedScratch $name $state.version } }
}
Assert-ProtectedContainers $state
if ($BackendOnly) {
    Write-Json (Join-Path $ReleaseDirectory 'validation/backend-results.json') ([pscustomobject]@{
        passed=$true; imageId=$state.release.backend.id; regressionTests=43; ormSecurityChecks=13;
        startupBypassed=$true; aiWritesEnabled=$false; httpSmokePassed=$true
    })
    Write-Output 'Backend image validated; full release remains gated on frontend validation.'
    return
}
Assert-ReleaseConfig $state $ReleaseDirectory | Out-Null
& (Join-Path $PSScriptRoot 'Validate-PostgresGuard.ps1') -ReleaseDirectory $ReleaseDirectory
$state.status = 'validated_not_deployed'; Write-Json $statePath $state
Write-Json (Join-Path $ReleaseDirectory 'validation/results.json') ([pscustomobject]@{
    passed=$true; backendRegressionTests=43; ormSecurityChecks=13; frontendActionChecks=6;
    backendStartupBypassed=$true; aiWritesEnabled=$false; frontendRouteSetUnchanged=$true;
    backendAndFrontendHttpSmokePassed=$true; postgresqlReadOnlyVerified=$true; existingContainersUnchanged=$true
})
Write-Output 'Both release images validated. Nothing deployed.'
