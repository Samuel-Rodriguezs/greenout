"""Hexdump estilo `hexdump -C` (gerar) e reconstrução dos bytes a partir do dump."""
from __future__ import annotations

import re


class ErroHexdump(ValueError):
    """Dump malformado."""


def hexdump(dados: bytes, largura: int = 16, deslocamento: int = 0) -> str:
    """Gera linhas 'offset  hex hex ...  |ascii|'; linhas repetidas viram '*' como no hexdump -C."""
    if largura < 1:
        raise ErroHexdump("largura deve ser positiva")
    linhas: list[str] = []
    anterior: bytes | None = None
    omitindo = False
    for i in range(0, len(dados), largura):
        bloco = dados[i:i + largura]
        if bloco == anterior and len(bloco) == largura:
            if not omitindo:
                linhas.append("*")
                omitindo = True
            continue
        omitindo = False
        anterior = bloco
        meio = largura // 2
        hexa = ""
        for j in range(largura):
            if j < len(bloco):
                hexa += f"{bloco[j]:02x} "
            else:
                hexa += "   "
            if j == meio - 1 and largura > 1:
                hexa += " "
        ascii_ = "".join(chr(b) if 32 <= b < 127 else "." for b in bloco)
        linhas.append(f"{i + deslocamento:08x}  {hexa} |{ascii_}|")
    linhas.append(f"{len(dados) + deslocamento:08x}")
    return "\n".join(linhas)


def reverter(dump: str) -> bytes:
    """Reconstrói os bytes a partir de um dump gerado por `hexdump` (largura detectada)."""
    saida = bytearray()
    ultimo_bloco = b""
    esperado: int | None = None
    pular = False
    base: int | None = None
    for n, linha in enumerate(dump.splitlines(), start=1):
        if not linha.strip():
            continue
        if linha.strip() == "*":
            pular = True
            continue
        m = re.fullmatch(r"([0-9a-fA-F]{8})(?:  ((?:[0-9a-fA-F]{2} ?| {2,3})*?) ?\|.*\|)?", linha)
        if not m:
            raise ErroHexdump(f"linha {n} inválida: {linha!r}")
        off = int(m.group(1), 16)
        if base is None:
            base = off
        pos = off - base
        if pular:
            falta = pos - len(saida)
            if falta < 0 or not ultimo_bloco or falta % len(ultimo_bloco):
                raise ErroHexdump(f"linha {n}: deslocamento incoerente após '*'")
            saida += ultimo_bloco * (falta // len(ultimo_bloco))
            pular = False
        if pos != len(saida):
            raise ErroHexdump(f"linha {n}: deslocamento {off:08x} inesperado")
        if m.group(2) is None:
            esperado = pos
            continue
        pares = re.findall(r"[0-9a-fA-F]{2}", m.group(2))
        bloco = bytes(int(p, 16) for p in pares)
        saida += bloco
        ultimo_bloco = bloco
    if pular:
        raise ErroHexdump("'*' sem linha seguinte")
    if esperado is not None and esperado != len(saida):
        raise ErroHexdump("deslocamento final não confere com o total de bytes")
    return bytes(saida)
