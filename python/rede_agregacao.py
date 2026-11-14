"""Agregação de prefixos IPv4 (supernetting): une blocos CIDR adjacentes."""
from __future__ import annotations

from rede_ipv4 import mascara_de_prefixo


def normalizar(prefixos: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Zera bits de host, remove duplicatas e blocos contidos em outros."""
    unicos = sorted({(ip & mascara_de_prefixo(p), p) for ip, p in prefixos})
    saida: list[tuple[int, int]] = []
    fim_anterior = -1
    for ip, p in unicos:
        fim = ip + (1 << (32 - p)) - 1
        if fim <= fim_anterior:
            continue  # contido no bloco anterior
        saida.append((ip, p))
        fim_anterior = fim
    return saida


def agregar(prefixos: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Menor lista de blocos CIDR cobrindo exatamente a mesma união."""
    atual = normalizar(prefixos)
    mudou = True
    while mudou:
        mudou = False
        novo: list[tuple[int, int]] = []
        i = 0
        while i < len(atual):
            ip, p = atual[i]
            if (
                i + 1 < len(atual)
                and p > 0
                and atual[i + 1][1] == p
                and ip % (1 << (33 - p)) == 0
                and atual[i + 1][0] == ip + (1 << (32 - p))
            ):
                novo.append((ip, p - 1))
                i += 2
                mudou = True
            else:
                novo.append((ip, p))
                i += 1
        atual = novo
    return atual


def supernet_minimo(prefixos: list[tuple[int, int]]) -> tuple[int, int]:
    """Menor bloco único que contém todos os prefixos (rota-resumo)."""
    if not prefixos:
        raise ValueError("lista vazia")
    ini = min(ip & mascara_de_prefixo(p) for ip, p in prefixos)
    fim = max((ip & mascara_de_prefixo(p)) + (1 << (32 - p)) - 1 for ip, p in prefixos)
    p = 32
    while p > 0 and (ini & mascara_de_prefixo(p)) != (fim & mascara_de_prefixo(p)):
        p -= 1
    return ini & mascara_de_prefixo(p), p
