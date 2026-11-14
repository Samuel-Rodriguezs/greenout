"""Serialização binária de linhas com tipos (INT, REAL, TEXT, BOOL) e bitmap de NULLs.

Formato: [bitmap de nulos: ceil(n/8) bytes][campos não nulos em ordem]
  INT  -> int64 little-endian      REAL -> float64
  BOOL -> 1 byte                    TEXT -> uint32 tamanho + UTF-8
"""
from __future__ import annotations

import struct
from typing import Any, Sequence

TIPOS = ("INT", "REAL", "TEXT", "BOOL")
_INT = struct.Struct("<q")
_REAL = struct.Struct("<d")
_LEN = struct.Struct("<I")
INT_MIN, INT_MAX = -(2**63), 2**63 - 1


class ErroSerializacaoLinha(Exception):
    pass


Esquema = Sequence[tuple[str, str]]


def validar_esquema(esquema: Esquema) -> None:
    nomes = set()
    for nome, tipo in esquema:
        if tipo not in TIPOS:
            raise ErroSerializacaoLinha(f"tipo desconhecido: {tipo}")
        if nome in nomes:
            raise ErroSerializacaoLinha(f"coluna duplicada: {nome}")
        nomes.add(nome)


def codificar_linha(esquema: Esquema, valores: Sequence[Any]) -> bytes:
    validar_esquema(esquema)
    if len(valores) != len(esquema):
        raise ErroSerializacaoLinha(f"esperados {len(esquema)} valores, recebidos {len(valores)}")
    bitmap = bytearray((len(esquema) + 7) // 8)
    corpo = bytearray()
    for i, ((nome, tipo), v) in enumerate(zip(esquema, valores)):
        if v is None:
            bitmap[i >> 3] |= 1 << (i & 7)
            continue
        if tipo == "INT":
            if isinstance(v, bool) or not isinstance(v, int):
                raise ErroSerializacaoLinha(f"{nome}: INT esperado, recebido {v!r}")
            if not INT_MIN <= v <= INT_MAX:
                raise ErroSerializacaoLinha(f"{nome}: inteiro fora de 64 bits")
            corpo += _INT.pack(v)
        elif tipo == "REAL":
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                raise ErroSerializacaoLinha(f"{nome}: REAL esperado, recebido {v!r}")
            corpo += _REAL.pack(float(v))
        elif tipo == "BOOL":
            if not isinstance(v, bool):
                raise ErroSerializacaoLinha(f"{nome}: BOOL esperado, recebido {v!r}")
            corpo.append(1 if v else 0)
        else:
            if not isinstance(v, str):
                raise ErroSerializacaoLinha(f"{nome}: TEXT esperado, recebido {v!r}")
            b = v.encode("utf-8")
            corpo += _LEN.pack(len(b)) + b
    return bytes(bitmap) + bytes(corpo)


def decodificar_linha(esquema: Esquema, dados: bytes) -> list[Any]:
    validar_esquema(esquema)
    n_bitmap = (len(esquema) + 7) // 8
    if len(dados) < n_bitmap:
        raise ErroSerializacaoLinha("dados truncados (bitmap)")
    bitmap, pos = dados[:n_bitmap], n_bitmap
    saida: list[Any] = []

    def pegar(n: int) -> bytes:
        nonlocal pos
        if pos + n > len(dados):
            raise ErroSerializacaoLinha("dados truncados")
        trecho = dados[pos:pos + n]
        pos += n
        return trecho

    for i, (nome, tipo) in enumerate(esquema):
        if bitmap[i >> 3] & (1 << (i & 7)):
            saida.append(None)
        elif tipo == "INT":
            saida.append(_INT.unpack(pegar(8))[0])
        elif tipo == "REAL":
            saida.append(_REAL.unpack(pegar(8))[0])
        elif tipo == "BOOL":
            b = pegar(1)[0]
            if b > 1:
                raise ErroSerializacaoLinha(f"{nome}: booleano inválido")
            saida.append(bool(b))
        else:
            n = _LEN.unpack(pegar(4))[0]
            try:
                saida.append(pegar(n).decode("utf-8"))
            except UnicodeDecodeError as e:
                raise ErroSerializacaoLinha(f"{nome}: UTF-8 inválido") from e
    if pos != len(dados):
        raise ErroSerializacaoLinha("bytes sobrando após a última coluna")
    return saida
