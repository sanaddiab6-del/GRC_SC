[CmdletBinding()]
param([Parameter(Mandatory)][string]$ReleaseDirectory)
. (Join-Path $PSScriptRoot 'Common.ps1')
$state = Read-Json (Join-Path $ReleaseDirectory 'state.json')
if ($state.status -ne 'validated_not_deployed') { throw 'Release validation is incomplete' }
$validation = Read-Json (Join-Path $ReleaseDirectory 'validation/results.json')
if (-not $validation.passed) { throw 'Validation did not pass' }
$pointer = Read-Json (Join-Path $ReleaseDirectory 'backup/latest-verified.json')
if ((File-Sha $pointer.manifestPath) -ne $pointer.sha256) { throw 'Backup evidence changed' }
$backup = Read-Json $pointer.manifestPath
if (-not $backup.verified -or (File-Sha $backup.file) -ne $backup.sha256) { throw 'Backup verification missing' }
$previous = Read-Json (Join-Path $ReleaseDirectory 'previous-images.json')
if ((File-Sha $previous.archive) -ne $previous.sha256) { throw 'Previous image archive changed' }
Assert-ReleaseConfig $state $ReleaseDirectory | Out-Null
Assert-ProtectedContainers $state
$files = @('state.json','source-manifest.json','release.override.yml','rollback.override.yml',
    'validation/results.json','backup/latest-verified.json','previous-images.json')
$files += @(Get-ChildItem -LiteralPath (Join-Path $ReleaseDirectory 'scripts') -File | ForEach-Object { 'scripts/' + $_.Name })
$hashes = @($files | ForEach-Object { [pscustomobject]@{ path=$_; sha256=(File-Sha (Join-Path $ReleaseDirectory $_)) } })
Write-Json (Join-Path $ReleaseDirectory 'seal.json') ([pscustomobject]@{
    version=$state.version; sealedUtc=[DateTime]::UtcNow.ToString('o'); files=$hashes; deploymentApproved=$false
})
Write-Output 'Release sealed for review. Deployment remains unapproved and has not run.'
