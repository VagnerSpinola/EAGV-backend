[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$HostName = 'psql-eagvbackenddev-ej3o1.postgres.database.azure.com',
    [string]$HostAddress = '191.232.254.48'
)

$currentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($currentIdentity)
$isAdministrator = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdministrator) {
    throw 'Execute este script em um PowerShell aberto como Administrador.'
}

$hostsPath = Join-Path $env:SystemRoot 'System32\drivers\etc\hosts'
$entry = "$HostAddress`t$HostName"
$existingLines = Get-Content -Path $hostsPath -ErrorAction Stop

$filteredLines = $existingLines | Where-Object {
    $_ -notmatch "(^|\s)$([Regex]::Escape($HostName))(\s|$)"
}

$updatedLines = @($filteredLines + $entry)

if ($PSCmdlet.ShouldProcess($hostsPath, "Adicionar ou atualizar entrada para $HostName")) {
    Set-Content -Path $hostsPath -Value $updatedLines -Encoding ASCII
    ipconfig /flushdns | Out-Null
    Write-Output "Entrada aplicada em $hostsPath"
    Write-Output $entry
}