<#
.SYNOPSIS
    Conta ocorrências de ERROR, WARN e INFO em um arquivo de log.
#>
param(
    [Parameter(Mandatory)][string]$Arquivo
)

if (-not (Test-Path $Arquivo)) {
    Write-Error "Arquivo não encontrado: $Arquivo"
    exit 1
}

$linhas = Get-Content $Arquivo
foreach ($nivel in "ERROR", "WARN", "INFO") {
    [pscustomobject]@{
        Nivel = $nivel
        Total = ($linhas | Select-String -Pattern "\b$nivel\b").Count
    }
}
