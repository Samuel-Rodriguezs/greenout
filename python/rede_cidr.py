"""CIDR e subnetting: rede, broadcast, hosts, divisão e VLSM."""
from __future__ import annotations

from typing import Iterator

from rede_ipv4 import formatar_ipv4, mascara_de_prefixo, parse_ipv4


def parse_cidr(texto: str) -> tuple[int, int]:
    """'10.1.2.3/8' -> (endereço, prefixo)."""
    ip, sep, pref = texto.partition("/")
    if not sep or not pref.isdigit():
        raise ValueError(f"CIDR inválido: {texto!r}")
    prefixo = int(pref)
    mascara_de_prefixo(prefixo)
    return parse_ipv4(ip), prefixo


def endereco_rede(ip: int, prefixo: int) -> int:
    return ip & mascara_de_prefixo(prefixo)


def broadcast(ip: int, prefixo: int) -> int:
    return endereco_rede(ip, prefixo) | (~mascara_de_prefixo(prefixo) & 0xFFFFFFFF)


def total_hosts(prefixo: int) -> int:
    """Hosts utilizáveis (/31 -> 2 por RFC 3021, /32 -> 1)."""
    mascara_de_prefixo(prefixo)
    if prefixo >= 31:
        return 2 if prefixo == 31 else 1
    return (1 << (32 - prefixo)) - 2


def hosts(ip: int, prefixo: int) -> Iterator[int]:
    rede = endereco_rede(ip, prefixo)
    bc = broadcast(ip, prefixo)
    if prefixo >= 31:
        yield from range(rede, bc + 1)
    else:
        yield from range(rede + 1, bc)


def dividir(ip: int, prefixo: int, novo_prefixo: int) -> list[tuple[int, int]]:
    """Divide a rede em sub-redes de tamanho igual com `novo_prefixo`."""
    if novo_prefixo < prefixo or novo_prefixo > 32:
        raise ValueError("novo prefixo deve ser >= prefixo e <= 32")
    rede = endereco_rede(ip, prefixo)
    passo = 1 << (32 - novo_prefixo)
    return [(rede + i * passo, novo_prefixo) for i in range(1 << (novo_prefixo - prefixo))]


def prefixo_para_hosts(qtd: int) -> int:
    """Maior prefixo (menor sub-rede) que comporta `qtd` hosts utilizáveis."""
    if qtd < 1:
        raise ValueError("qtd deve ser >= 1")
    for p in range(30, -1, -1):
        if total_hosts(p) >= qtd:
            return p
    raise ValueError("qtd grande demais")


def vlsm(ip: int, prefixo: int, demandas: dict[str, int]) -> dict[str, tuple[int, int]]:
    """Aloca sub-redes por demanda de hosts, da maior para a menor."""
    base = endereco_rede(ip, prefixo)
    limite = broadcast(ip, prefixo)
    cursor = base
    saida: dict[str, tuple[int, int]] = {}
    for nome, qtd in sorted(demandas.items(), key=lambda kv: (-kv[1], kv[0])):
        p = prefixo_para_hosts(qtd)
        tam = 1 << (32 - p)
        if cursor + tam - 1 > limite:
            raise ValueError(f"espaço insuficiente para {nome!r}")
        saida[nome] = (cursor, p)
        cursor += tam
    return saida


def formatar_cidr(ip: int, prefixo: int) -> str:
    return f"{formatar_ipv4(ip)}/{prefixo}"
