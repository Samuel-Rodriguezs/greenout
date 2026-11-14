"""Checksum de Internet (RFC 1071): soma em complemento de um de 16 bits."""
from __future__ import annotations


def soma_complemento_um(dados: bytes, inicial: int = 0) -> int:
    """Soma palavras de 16 bits (big-endian) com carry circular."""
    if len(dados) % 2:
        dados += b"\x00"
    total = inicial
    for i in range(0, len(dados), 2):
        total += (dados[i] << 8) | dados[i + 1]
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return total


def checksum(dados: bytes) -> int:
    """Checksum a ser colocado no cabeçalho (campo zerado durante o cálculo)."""
    return ~soma_complemento_um(dados) & 0xFFFF


def verificar(dados: bytes) -> bool:
    """Dados já contendo o checksum: a soma deve resultar em 0xFFFF."""
    return soma_complemento_um(dados) == 0xFFFF


def atualizar_incremental(checksum_antigo: int, palavra_antiga: int, palavra_nova: int) -> int:
    """RFC 1624: HC' = ~(~HC + ~m + m') sem recalcular tudo."""
    total = (~checksum_antigo & 0xFFFF) + (~palavra_antiga & 0xFFFF) + (palavra_nova & 0xFFFF)
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return ~total & 0xFFFF
