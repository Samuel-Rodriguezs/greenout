"""CRC32 (tabela) e Adler32 puros. Didático; compare com zlib."""
from __future__ import annotations


def _tabela() -> list[int]:
    t = []
    for i in range(256):
        c = i
        for _ in range(8):
            c = (c >> 1) ^ 0xEDB88320 if c & 1 else c >> 1
        t.append(c)
    return t


_TAB = _tabela()


def crc32(dados: bytes, inicial: int = 0) -> int:
    """CRC32 IEEE; `inicial` permite cálculo incremental."""
    c = inicial ^ 0xFFFFFFFF
    for b in dados:
        c = _TAB[(c ^ b) & 0xFF] ^ (c >> 8)
    return c ^ 0xFFFFFFFF


def adler32(dados: bytes, inicial: int = 1) -> int:
    a = inicial & 0xFFFF
    b = (inicial >> 16) & 0xFFFF
    for x in dados:
        a = (a + x) % 65521
        b = (b + a) % 65521
    return (b << 16) | a
