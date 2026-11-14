<#
.SYNOPSIS
    Mostra o espaço total, usado e livre dos discos/volumes.
.DESCRIPTION
    Usa Get-PSDrive (multiplataforma) e emite um objeto por unidade com
    tamanhos em GB e percentual livre. Pode alertar unidades abaixo de um limite.
.PARAMETER LimitePercentualLivre
    Se informado, retorna apenas unidades com percentual livre menor ou igual.
.EXAMPLE
    ./Get-EspacoDisco.ps1
.EXAMPLE
    ./Get-EspacoDisco.ps1 -LimitePercentualLivre 15
#>
[CmdletBinding()]
param(
    [ValidateRange(0, 100)][double]$LimitePercentualLivre = 100
)

$ErrorActionPreference = 'Stop'

try {
    $unidades = Get-PSDrive -PSProvider FileSystem |
        Where-Object { $null -ne $_.Used -and $null -ne $_.Free -and ($_.Used + $_.Free) -gt 0 }
}
catch {
    Write-Error "Falha ao consultar os discos: $($_.Exception.Message)"
    exit 1
}

foreach ($u in $unidades) {
    $total = $u.Used + $u.Free
    $percLivre = [math]::Round(($u.Free / $total) * 100, 1)
    if ($percLivre -le $LimitePercentualLivre) {
        [pscustomobject]@{
            Unidade     = $u.Name
            TotalGB     = [math]::Round($total / 1GB, 2)
            UsadoGB     = [math]::Round($u.Used / 1GB, 2)
            LivreGB     = [math]::Round($u.Free / 1GB, 2)
            PercLivre   = $percLivre
        }
    }
}
