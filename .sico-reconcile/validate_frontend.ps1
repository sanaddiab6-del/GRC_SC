$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$snapshot = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'current.txt'))
$manifest = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText((Join-Path $snapshot 'manifest.json')))
$sources = @{}
foreach ($entry in $manifest) {
    if (!$entry.Path.StartsWith('frontend/')) { continue }
    $source = Join-Path $root $entry.Path
    $sources[$entry.Path] = [Convert]::ToBase64String([IO.File]::ReadAllBytes($source))
}
$payload = @{
    sources=$sources
    checkScript=[Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $root 'tools/check_sico_ai_frontend.cjs')))
} | ConvertTo-Json -Depth 6 -Compress
$encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($payload))
$script = "const PAYLOAD=JSON.parse(Buffer.from('$encoded','base64').toString('utf8'));`n" + [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'validate_frontend.cjs'))
$raw = $script | docker exec -i amro-frontend node
$exitCode = $LASTEXITCODE
$utf8 = New-Object Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $snapshot 'frontend-validation.json'),($raw -join "`n"),$utf8)
Write-Output ($raw -join "`n")
if ($exitCode -ne 0) { throw "Frontend checks failed ($exitCode)" }
