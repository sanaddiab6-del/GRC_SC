[CmdletBinding()]
param([Parameter(Mandatory)][string]$ReleaseDirectory)
. (Join-Path $PSScriptRoot 'Common.ps1')
if (Test-Path -LiteralPath (Join-Path $ReleaseDirectory 'seal.json')) { throw 'Refusing to modify sealed scripts' }
$state = Read-Json (Join-Path $ReleaseDirectory 'state.json')
if ((Split-Path -Leaf $ReleaseDirectory) -ne $state.version) { throw 'Unexpected release-directory identity' }
$destination = Join-Path $ReleaseDirectory 'scripts'
$hashes = @()
foreach ($file in (Get-ChildItem -LiteralPath $PSScriptRoot -File)) {
    if ($file.Extension -eq '.ps1') {
        $tokens=$null; $errors=$null
        [Management.Automation.Language.Parser]::ParseFile($file.FullName,[ref]$tokens,[ref]$errors) | Out-Null
        if ($errors.Count) { throw "PowerShell syntax failed: $($file.Name)" }
    }
    $target = Join-Path $destination $file.Name
    if ([IO.Path]::GetFullPath($file.FullName) -ne [IO.Path]::GetFullPath($target)) {
        Copy-Item -LiteralPath $file.FullName -Destination $target
    }
    $hashes += [pscustomobject]@{ path='scripts/' + $file.Name; sha256=(File-Sha $target) }
}
Write-Json (Join-Path $ReleaseDirectory 'script-manifest.json') $hashes
Write-Output 'Reviewed scripts staged; all PowerShell files parsed. No services changed.'
