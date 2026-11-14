<#
.SYNOPSIS
    Testa se portas TCP de um host estão abertas.
.DESCRIPTION
    Tenta conectar em cada porta com timeout usando System.Net.Sockets.TcpClient
    e emite um objeto por porta com o resultado.
.PARAMETER Servidor
    Nome ou IP do host. Padrão: localhost.
.PARAMETER Portas
    Lista de portas TCP (1-65535).
.PARAMETER TimeoutMs
    Tempo máximo de espera por porta, em milissegundos. Padrão: 1000.
.EXAMPLE
    ./Test-Portas.ps1 -Portas 22,80,443
.EXAMPLE
    ./Test-Portas.ps1 -Servidor exemplo.com -Portas 443 -TimeoutMs 3000
#>
[CmdletBinding()]
param(
    [string]$Servidor = 'localhost',
    [Parameter(Mandatory)][ValidateRange(1, 65535)][int[]]$Portas,
    [ValidateRange(50, 60000)][int]$TimeoutMs = 1000
)

foreach ($porta in $Portas) {
    $cliente = [System.Net.Sockets.TcpClient]::new()
    $aberta = $false
    $erro = $null
    try {
        $tarefa = $cliente.ConnectAsync($Servidor, $porta)
        if ($tarefa.Wait($TimeoutMs)) {
            $aberta = $cliente.Connected
        }
        else {
            $erro = 'timeout'
        }
    }
    catch {
        $erro = $_.Exception.GetBaseException().Message
    }
    finally {
        $cliente.Dispose()
    }

    [pscustomobject]@{
        Servidor = $Servidor
        Porta = $porta
        Aberta = $aberta
        Erro  = $erro
    }
}
