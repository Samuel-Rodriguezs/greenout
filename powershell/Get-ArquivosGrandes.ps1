<#
.SYNOPSIS
    Lista os maiores arquivos de uma pasta.
.EXAMPLE
    ./Get-ArquivosGrandes.ps1 -Caminho . -Top 5
#>
param(
    [string]$Caminho = ".",
    [int]$Top = 10
)

Get-ChildItem -Path $Caminho -File -Recurse -ErrorAction SilentlyContinue |
    Sort-Object Length -Descending |
    Select-Object -First $Top Name, @{N = "MB"; E = { [math]::Round($_.Length / 1MB, 2) }}, DirectoryName
