<#
.SYNOPSIS
    Converte um arquivo CSV em JSON.
.DESCRIPTION
    Lê o CSV com Import-Csv e grava (ou emite no pipeline) um array JSON.
    Suporta -WhatIf quando grava em arquivo.
.PARAMETER Arquivo
    Caminho do CSV de entrada.
.PARAMETER Saida
    Caminho do JSON de saída. Se omitido, escreve o JSON na saída padrão.
.PARAMETER Delimitador
    Delimitador do CSV. Padrão: vírgula.
.EXAMPLE
    ./Convert-CsvParaJson.ps1 -Arquivo dados.csv -Saida dados.json
.EXAMPLE
    ./Convert-CsvParaJson.ps1 -Arquivo dados.csv -Delimitador ';'
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)][string]$Arquivo,
    [string]$Saida,
    [ValidateLength(1, 1)][string]$Delimitador = ','
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $Arquivo -PathType Leaf)) {
    Write-Error "Arquivo não encontrado: $Arquivo"
    exit 1
}

try {
    $linhas = @(Import-Csv -LiteralPath $Arquivo -Delimiter $Delimitador -Encoding UTF8)
    $json = ConvertTo-Json -InputObject $linhas -Depth 5

    if ($Saida) {
        if ($PSCmdlet.ShouldProcess($Saida, 'Gravar JSON')) {
            Set-Content -LiteralPath $Saida -Value $json -Encoding UTF8
            Write-Verbose "$($linhas.Count) registro(s) gravado(s) em $Saida"
        }
    }
    else {
        Write-Output $json
    }
}
catch {
    Write-Error "Falha na conversão: $($_.Exception.Message)"
    exit 1
}
