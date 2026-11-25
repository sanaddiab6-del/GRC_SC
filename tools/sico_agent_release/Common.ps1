Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-Docker {
    param([Parameter(Mandatory)][string[]]$Arguments)
    $output = & docker @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Docker failed (exit $LASTEXITCODE): $($Arguments[0])" }
    return $output
}

function Read-Container([string]$Name) {
    $items = Invoke-Docker @('inspect', $Name) | ConvertFrom-Json
    return @($items)[0]
}

function Read-Environment($Container) {
    $map = @{}
    foreach ($entry in $Container.Config.Env) {
        foreach ($line in ($entry -split "`n")) {
            $pair = $line.TrimEnd("`r") -split '=', 2
            if ($pair.Count -eq 2) { $map[$pair[0]] = $pair[1] }
        }
    }
    return $map
}

function Write-Json([string]$Path, $Value) {
    [IO.File]::WriteAllText($Path, ($Value | ConvertTo-Json -Depth 80), [Text.UTF8Encoding]::new($false))
}

function Read-Json([string]$Path) { $decoded = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json; return $decoded }
function File-Sha([string]$Path) { return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }
function Text-Sha([string]$Path) {
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [Text.Encoding]::UTF8.GetBytes([IO.File]::ReadAllText($Path).Replace("`r`n","`n"))
        return ([BitConverter]::ToString($algorithm.ComputeHash($bytes))).Replace('-','').ToLowerInvariant()
    } finally { $algorithm.Dispose() }
}

function Assert-Target($Container, [string]$Service) {
    if ($Container.Config.Labels.'com.docker.compose.project' -ne 'grc_amro_test' -or
        $Container.Config.Labels.'com.docker.compose.service' -ne $Service -or
        $Container.Name -ne "/amro-$Service") { throw "Unexpected target for $Service" }
}

function Snapshot-Containers {
    $ids = @(Invoke-Docker @('ps', '-q'))
    if (-not $ids.Count) { throw 'No running containers' }
    $items = Invoke-Docker (@('inspect') + $ids) | ConvertFrom-Json
    foreach ($item in $items) {
        [pscustomobject]@{ name=$item.Name.TrimStart('/'); id=$item.Id; image=$item.Image;
            started=$item.State.StartedAt; project=$(if ($item.Config.Labels -and $item.Config.Labels.PSObject.Properties['com.docker.compose.project']) { $item.Config.Labels.'com.docker.compose.project' } else { '' }) }
    }
}

function Assert-ProtectedContainers($State, [switch]$AllowAppReplacement) {
    foreach ($prior in $State.runningContainers) {
        if ($AllowAppReplacement -and $prior.name -in @('amro-backend','amro-frontend')) { continue }
        $current = Read-Container $prior.name
        if ($current.Id -ne $prior.id -or $current.Image -ne $prior.image -or
            $current.State.StartedAt -ne $prior.started -or -not $current.State.Running) {
            throw "Container drift detected: $($prior.name). Refusing to proceed."
        }
    }
}

function Compose-Args($State, [string]$Override) {
    $argsList = @('compose','--project-name','grc_amro_test','--project-directory',$State.repository)
    foreach ($file in $State.composeFiles) {
        if ((File-Sha $file.path) -ne $file.sha256) { throw "Compose file changed: $($file.path)" }
        $argsList += @('-f', $file.path)
    }
    if ($Override) { $argsList += @('-f', $Override) }
    return $argsList
}

function Changed-Paths($Before, $After, [string]$Prefix='') {
    if ($null -eq $Before -or $null -eq $After) {
        if (($Before | ConvertTo-Json -Depth 80 -Compress) -ne ($After | ConvertTo-Json -Depth 80 -Compress)) { $Prefix }
        return
    }
    if ($Before -is [pscustomobject] -and $After -is [pscustomobject]) {
        $keys = @(@($Before.PSObject.Properties | ForEach-Object Name) + @($After.PSObject.Properties | ForEach-Object Name) | Sort-Object -Unique)
        foreach ($key in $keys) {
            $left = $Before.PSObject.Properties[$key]; $right = $After.PSObject.Properties[$key]
            Changed-Paths $(if ($left) { $left.Value } else { $null }) $(if ($right) { $right.Value } else { $null }) "$Prefix.$key"
        }
    } elseif (($Before | ConvertTo-Json -Depth 80 -Compress) -ne ($After | ConvertTo-Json -Depth 80 -Compress)) { $Prefix }
}

function Assert-ReleaseConfig($State, [string]$ReleaseDirectory) {
    $baseArgs = @(Compose-Args $State '')
    $base = Invoke-Docker ($baseArgs + @('config','--format','json')) | ConvertFrom-Json
    $releaseArgs = @(Compose-Args $State (Join-Path $ReleaseDirectory 'release.override.yml'))
    $effective = Invoke-Docker ($releaseArgs + @('config','--format','json')) | ConvertFrom-Json
    $allowed = @('.services.backend.image','.services.frontend.image',
        '.services.backend.entrypoint','.services.backend.command',
        '.services.backend.environment.DJANGO_SETTINGS_MODULE',
        '.services.backend.environment.SICO_ENGAGEMENT_COMMITS_ENABLED',
        '.services.backend.environment.FORCE_CREATE_ADMIN')
    $changes = @(Changed-Paths $base $effective)
    foreach ($change in $changes) { if ($change -notin $allowed) { throw "Unexpected Compose change: $change" } }
    if ($effective.services.backend.image -ne $State.release.backend.reference -or
        $effective.services.frontend.image -ne $State.release.frontend.reference -or
        @($effective.services.backend.entrypoint)[0] -ne '/code/sico-agent-start.sh' -or
        @($effective.services.backend.command).Count -ne 0 -or
        $effective.services.backend.environment.DJANGO_SETTINGS_MODULE -ne 'ciso_assistant.sico_agent_release_settings') {
        throw 'Unsafe effective release configuration'
    }
    return $changes
}

function Assert-Image([string]$Reference, [string]$ExpectedId) {
    $actual = (Invoke-Docker @('image','inspect',$Reference,'--format','{{.Id}}')).Trim()
    if ($actual -ne $ExpectedId) { throw "Image identity changed: $Reference" }
}

function Quote-WindowsArgument([string]$Value) {
    # CommandLineToArgvW quoting, for binary-safe ProcessStartInfo on Windows PS 5.
    if ($Value -notmatch '[\s"]' -and $Value.Length) { return $Value }
    $escaped = [regex]::Replace($Value, '(\\*)"', '$1$1\"')
    $escaped = [regex]::Replace($escaped, '(\\+)$', '$1$1')
    return '"' + $escaped + '"'
}

function Export-DockerBinary([string[]]$Arguments, [string]$Destination) {
    if (Test-Path -LiteralPath $Destination) { throw "Refusing to overwrite $Destination" }
    $info = [Diagnostics.ProcessStartInfo]::new()
    $info.FileName = (Get-Command docker).Source
    $info.Arguments = (($Arguments | ForEach-Object { Quote-WindowsArgument $_ }) -join ' ')
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $process = [Diagnostics.Process]::new(); $process.StartInfo = $info
    if (-not $process.Start()) { throw 'Could not start Docker' }
    $errors = $process.StandardError.ReadToEndAsync()
    $stream = [IO.File]::Open($Destination, [IO.FileMode]::CreateNew)
    try { $process.StandardOutput.BaseStream.CopyTo($stream) } finally { $stream.Dispose() }
    $process.WaitForExit()
    if ($process.ExitCode -ne 0) { throw "Binary export failed: $($errors.Result)" }
}

function Remove-OwnedScratch([string]$Name, [string]$Version) {
    $item = Read-Container $Name
    if ($item.Config.Labels.'sico.agent.scratch' -ne $Version -or $Name -notlike 'sico-agent-*') {
        throw "Refusing scratch cleanup: $Name"
    }
    foreach ($mount in $item.Mounts) {
        if ($mount.Type -eq 'volume' -and -not ($mount.Name -eq 'sico_ai_next_preview_modules' -and
            $mount.RW -eq $false -and $mount.Destination -in @('/deps','/tmp/frontend/node_modules'))) {
            throw 'Unexpected Docker volume on scratch container'
        }
    }
    Invoke-Docker @('rm','--force',$Name) | Out-Null
}

function Read-DockerLogs([string]$Name) {
    $ErrorActionPreference = 'Continue'
    $lines = & docker logs $Name 2>&1
    if ($LASTEXITCODE -ne 0) { throw 'Could not read disposable container log' }
    return @($lines | ForEach-Object { [string]$_ })
}
