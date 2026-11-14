<#
.SYNOPSIS
    Lista os processos que mais consomem memória.
.DESCRIPTION
    Ordena os processos por working set e emite os N primeiros com memória
    em MB e tempo total de CPU.
.PARAMETER Quantidade
    Quantos processos retornar. Padrão: 10.
.PARAMETER MinimoMB
    Ignora processos com memória menor que este valor. Padrão: 0.
.EXAMPLE
    ./Get-ProcessosPesados.ps1 -Quantidade 5
.EXAMPLE
    ./Get-ProcessosPesados.ps1 -MinimoMB 200
#>
[CmdletBinding()]
param(
    [ValidateRange(1, 1000)][int]$Quantidade = 10,
    [ValidateRange(0, [int]::MaxValue)][int]$MinimoMB = 0
)

try {
    $processos = Get-Process -ErrorAction Stop
}
catch {
    Write-Error "Falha ao listar processos: $($_.Exception.Message)"
    exit 1
}

$processos |
    Where-Object { ($_.WorkingSet64 / 1MB) -ge $MinimoMB } |
    Sort-Object WorkingSet64 -Descending |
    Select-Object -First $Quantidade |
    ForEach-Object {
        [pscustomobject]@{
            Id         = $_.Id
            Nome       = $_.ProcessName
            MemoriaMB  = [math]::Round($_.WorkingSet64 / 1MB, 1)
            CpuSegundos = if ($null -ne $_.CPU) { [math]::Round($_.CPU, 1) } else { 0 }
        }
    }
