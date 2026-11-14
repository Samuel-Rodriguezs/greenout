"""Parser e formatador de expressões de tamanho ("1.5GB", "2 MiB", "512k")."""
from __future__ import annotations

import re


class ErroTamanho(ValueError):
    """Expressão de tamanho inválida."""


_SI = {"": 1, "K": 10**3, "M": 10**6, "G": 10**9, "T": 10**12, "P": 10**15}
_BIN = {"": 1, "K": 2**10, "M": 2**20, "G": 2**30, "T": 2**40, "P": 2**50}
_RE = re.compile(r"\s*(\d+(?:[.,]\d+)?|[.,]\d+)\s*([KMGTP]?)(I?)([B]?)\s*", re.I)


def parse(texto: str, binario_por_padrao: bool = False) -> int:
    """Converte para bytes. 'KB' é 1000 e 'KiB' é 1024; 'K'/'M' sozinhos seguem `binario_por_padrao`."""
    m = _RE.fullmatch(texto)
    if not m:
        raise ErroTamanho(f"tamanho inválido: {texto!r}")
    num, prefixo, i, b = m.groups()
    prefixo = prefixo.upper()
    if i and not prefixo:
        raise ErroTamanho(f"unidade inválida: {texto!r}")
    binario = bool(i) or (binario_por_padrao and not b)
    tabela = _BIN if binario else _SI
    valor = float(num.replace(",", ".")) * tabela[prefixo]
    # evita erros de ponto flutuante com frações exatas
    inteiro = round(valor)
    if abs(valor - inteiro) > 1e-6 * max(1.0, valor):
        inteiro = int(valor)
    return inteiro


def formatar(n: int, binario: bool = False, casas: int = 1) -> str:
    """Formata bytes de forma legível: 1500 -> '1.5 KB' (ou '1.46 KiB' no modo binário)."""
    if n < 0:
        raise ErroTamanho("tamanho negativo")
    base = 1024 if binario else 1000
    sufixo = "iB" if binario else "B"
    unidades = ["", "K", "M", "G", "T", "P"]
    if n < base:
        return f"{n} B"
    valor = float(n)
    idx = 0
    while valor >= base and idx < len(unidades) - 1:
        valor /= base
        idx += 1
    if round(valor, casas) >= base and idx < len(unidades) - 1:
        valor /= base
        idx += 1
    txt = f"{valor:.{casas}f}".rstrip("0").rstrip(".") if casas else f"{valor:.0f}"
    return f"{txt} {unidades[idx]}{sufixo}"
