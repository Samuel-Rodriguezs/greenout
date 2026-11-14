"""Código de Hamming(7,4): corrige 1 erro e detecta/corrige por síndrome."""
from __future__ import annotations

# Posições 1..7: p1 p2 d1 p4 d2 d3 d4 (paridade nas potências de 2).


def codificar_nibble(d: list[int]) -> list[int]:
    """4 bits de dados -> palavra de 7 bits."""
    if len(d) != 4 or any(b not in (0, 1) for b in d):
        raise ValueError("são necessários 4 bits")
    d1, d2, d3, d4 = d
    p1 = d1 ^ d2 ^ d4
    p2 = d1 ^ d3 ^ d4
    p4 = d2 ^ d3 ^ d4
    return [p1, p2, d1, p4, d2, d3, d4]


def sindrome(w: list[int]) -> int:
    """0 se íntegra; senão, a posição (1..7) do bit com erro."""
    if len(w) != 7 or any(b not in (0, 1) for b in w):
        raise ValueError("palavra deve ter 7 bits")
    s1 = w[0] ^ w[2] ^ w[4] ^ w[6]
    s2 = w[1] ^ w[2] ^ w[5] ^ w[6]
    s4 = w[3] ^ w[4] ^ w[5] ^ w[6]
    return s1 + 2 * s2 + 4 * s4


def decodificar_palavra(w: list[int]) -> tuple[list[int], int]:
    """Retorna (4 bits de dados corrigidos, posição corrigida ou 0)."""
    pos = sindrome(w)
    c = list(w)
    if pos:
        c[pos - 1] ^= 1
    return [c[2], c[4], c[5], c[6]], pos


def bytes_para_bits(dados: bytes) -> list[int]:
    return [(b >> i) & 1 for b in dados for i in range(7, -1, -1)]


def bits_para_bytes(bits: list[int]) -> bytes:
    if len(bits) % 8:
        raise ValueError("quantidade de bits deve ser múltipla de 8")
    return bytes(
        sum(bit << (7 - k) for k, bit in enumerate(bits[i: i + 8]))
        for i in range(0, len(bits), 8)
    )


def codificar(dados: bytes) -> list[int]:
    """Cada byte vira 14 bits (dois nibbles, alto primeiro)."""
    bits = bytes_para_bits(dados)
    saida: list[int] = []
    for i in range(0, len(bits), 4):
        saida += codificar_nibble(bits[i: i + 4])
    return saida


def decodificar(bits: list[int]) -> tuple[bytes, int]:
    """Retorna (dados, nº de palavras corrigidas)."""
    if len(bits) % 14:
        raise ValueError("quantidade de bits deve ser múltipla de 14")
    dados: list[int] = []
    corrigidas = 0
    for i in range(0, len(bits), 7):
        nibble, pos = decodificar_palavra(bits[i: i + 7])
        dados += nibble
        corrigidas += 1 if pos else 0
    return bits_para_bytes(dados), corrigidas
