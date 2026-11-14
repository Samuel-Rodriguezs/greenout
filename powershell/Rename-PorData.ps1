<#
.SYNOPSIS
    Prefixa arquivos com a data de modificação (yyyy-MM-dd_nome).
    Use -WhatIf para simular sem renomear.
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$Caminho = "."
)

Get-ChildItem -Path $Caminho -File | ForEach-Object {
    $novo = "{0:yyyy-MM-dd}_{1}" -f $_.LastWriteTime, $_.Name
    if ($PSCmdlet.ShouldProcess($_.FullName, "Renomear para $novo")) {
        Rename-Item -Path $_.FullName -NewName $novo
    }
}
