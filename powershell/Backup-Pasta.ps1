<#
.SYNOPSIS
    Compacta uma pasta em um arquivo .zip com carimbo de data/hora.
.DESCRIPTION
    Usa Compress-Archive. Suporta -WhatIf e -Confirm. Opcionalmente mantém
    apenas os N backups mais recentes do mesmo prefixo.
.PARAMETER Origem
    Pasta a ser copiada.
.PARAMETER Destino
    Pasta onde o zip será criado (criada se não existir).
.PARAMETER Manter
    Se > 0, mantém apenas os N backups mais recentes. Padrão: 0 (mantém todos).
.EXAMPLE
    ./Backup-Pasta.ps1 -Origem ./projeto -Destino ./backups -WhatIf
.EXAMPLE
    ./Backup-Pasta.ps1 -Origem ./projeto -Destino ./backups -Manter 5
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)][string]$Origem,
    [Parameter(Mandatory)][string]$Destino,
    [ValidateRange(0, 1000)][int]$Manter = 0
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $Origem -PathType Container)) {
    Write-Error "Pasta de origem não encontrada: $Origem"
    exit 1
}

try {
    $nome = (Get-Item -LiteralPath $Origem).Name
    $carimbo = Get-Date -Format 'yyyyMMdd-HHmmss'
    $arquivo = Join-Path $Destino "$nome-$carimbo.zip"

    if ($PSCmdlet.ShouldProcess($arquivo, "Compactar '$Origem'")) {
        if (-not (Test-Path -LiteralPath $Destino)) {
            New-Item -ItemType Directory -Path $Destino | Out-Null
        }
        Compress-Archive -Path (Join-Path $Origem '*') -DestinationPath $arquivo
        Write-Output (Get-Item -LiteralPath $arquivo)

        if ($Manter -gt 0) {
            Get-ChildItem -LiteralPath $Destino -Filter "$nome-*.zip" |
                Sort-Object LastWriteTime -Descending |
                Select-Object -Skip $Manter |
                Remove-Item -Force
        }
    }
}
catch {
    Write-Error "Falha no backup: $($_.Exception.Message)"
    exit 1
}
