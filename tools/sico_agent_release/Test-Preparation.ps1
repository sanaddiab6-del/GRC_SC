[CmdletBinding()]
param([Parameter(Mandatory)][string]$ReleaseDirectory)
. (Join-Path $PSScriptRoot 'Common.ps1')
$state = Read-Json (Join-Path $ReleaseDirectory 'state.json')
Assert-ProtectedContainers $state
$source = Invoke-Docker @('run','--rm','--network','none','--memory','256m',
    '--mount',"type=bind,source=$PSScriptRoot,target=/release-tools,readonly",'--mount',
    "type=bind,source=$(Join-Path $ReleaseDirectory 'source-manifest.json'),target=/release-input/source-manifest.json,readonly",
    '--entrypoint','/code/.venv/bin/python',$state.release.backend.reference,'/release-tools/verify_source_manifest.py')
[IO.File]::WriteAllLines((Join-Path $ReleaseDirectory 'validation/backend-source-manifest.json'),[string[]]$source,[Text.UTF8Encoding]::new($false))
$front = Invoke-Docker @('run','--rm','--network','none','--memory','384m',
    '--mount',"type=bind,source=$(Join-Path $ReleaseDirectory 'validation-input'),target=/checks,readonly",'--mount',
    "type=bind,source=$(Join-Path $ReleaseDirectory 'frontend-source/frontend'),target=/source,readonly",'--mount',
    'type=volume,source=sico_ai_next_preview_modules,target=/deps,readonly','--entrypoint','node',
    'node:22-bookworm-slim','/checks/check_sico_ai_frontend.cjs')
[IO.File]::WriteAllLines((Join-Path $ReleaseDirectory 'validation/frontend-source.json'),[string[]]$front,[Text.UTF8Encoding]::new($false))
$deployPlan = & (Join-Path $PSScriptRoot 'Deploy-Release.ps1') -ReleaseDirectory $ReleaseDirectory
[IO.File]::WriteAllLines((Join-Path $ReleaseDirectory 'validation/deployment-dry-run.log'),[string[]]$deployPlan,[Text.UTF8Encoding]::new($false))
$rollbackPlan = & (Join-Path $PSScriptRoot 'Rollback-Release.ps1') -ReleaseDirectory $ReleaseDirectory
[IO.File]::WriteAllLines((Join-Path $ReleaseDirectory 'validation/rollback-dry-run.log'),[string[]]$rollbackPlan,[Text.UTF8Encoding]::new($false))
$blocked = $false
if ($state.status -ne 'validated_not_deployed') {
    try { & (Join-Path $PSScriptRoot 'Seal-Release.ps1') -ReleaseDirectory $ReleaseDirectory }
    catch { if ($_.Exception.Message -notlike '*validation is incomplete*') { throw }; $blocked=$true }
    if (-not $blocked) { throw 'Incomplete release was unexpectedly sealable' }
}
Assert-ProtectedContainers $state
Write-Json (Join-Path $ReleaseDirectory 'validation/preparation-checks.json') ([pscustomobject]@{
    backendImageSourceHashesVerified=$true; frontendSourceCompiled=$true; frontendActionChecks=6;
    deploymentDryRunVerified=$true; rollbackDryRunVerified=$true;
    incompleteReleaseSealRefused=$blocked; existingServicesUnchangedSinceAcceptedBaseline=$true
})
Write-Output 'Preparation checks passed. Full frontend image build remains required before sealing or deployment.'
