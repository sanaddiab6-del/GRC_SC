[CmdletBinding()]
param([Parameter(Mandatory)][string]$ReleaseDirectory)
. (Join-Path $PSScriptRoot 'Common.ps1')
$state = Read-Json (Join-Path $ReleaseDirectory 'state.json')
Assert-Image $state.previous.backend.rollbackReference $state.previous.backend.id
Assert-Image $state.previous.frontend.rollbackReference $state.previous.frontend.id
$archive = Join-Path $ReleaseDirectory 'previous-images.tar'
if (Test-Path -LiteralPath $archive) { throw 'Refusing to overwrite an existing image archive' }
$imageSize = 0L
foreach ($reference in @($state.previous.backend.rollbackReference,$state.previous.frontend.rollbackReference)) {
    $imageSize += [long](Invoke-Docker @('image','inspect',$reference,'--format','{{.Size}}'))
}
$drive = [IO.DriveInfo]::new([IO.Path]::GetPathRoot($ReleaseDirectory))
if ($drive.AvailableFreeSpace -lt ($imageSize * 1.2)) { throw 'Insufficient free space for a safe image archive' }
Invoke-Docker @('image','save','--output',$archive,$state.previous.backend.rollbackReference,$state.previous.frontend.rollbackReference) | Out-Null
& tar -tf $archive | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Image archive is not readable' }
Write-Json (Join-Path $ReleaseDirectory 'previous-images.json') ([pscustomobject]@{
    archive=$archive; sha256=(File-Sha $archive); bytes=(Get-Item -LiteralPath $archive).Length;
    backendId=$state.previous.backend.id; frontendId=$state.previous.frontend.id
})
Write-Output "Exact previous images archived: $archive"
