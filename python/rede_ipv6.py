"""IPv6: expansão e compactação de endereços (RFC 5952)."""
from __future__ import annotations


def _grupos(texto: str) -> list[int]:
    texto = texto.strip().lower()
    if not texto:
        raise ValueError("endereço vazio")
    if texto.count("::") > 1 or ":::" in texto:
        raise ValueError("'::' só pode aparecer uma vez")
    # sufixo IPv4 embutido (::ffff:1.2.3.4)
    if "." in texto:
        cabeca, _, v4 = texto.rpartition(":")
        octetos = v4.split(".")
        if len(octetos) != 4 or not all(o.isdigit() and int(o) < 256 for o in octetos):
            raise ValueError("IPv4 embutido inválido")
        a, b, c, d = (int(o) for o in octetos)
        texto = f"{cabeca}:{(a << 8) | b:x}:{(c << 8) | d:x}"
    if "::" in texto:
        esq, _, dir_ = texto.partition("::")
        g_esq = esq.split(":") if esq else []
        g_dir = dir_.split(":") if dir_ else []
        falta = 8 - len(g_esq) - len(g_dir)
        if falta < 1:
            raise ValueError("'::' sem grupos a omitir")
        partes = g_esq + ["0"] * falta + g_dir
    else:
        partes = texto.split(":")
    if len(partes) != 8:
        raise ValueError("número de grupos inválido")
    saida = []
    for p in partes:
        if not 1 <= len(p) <= 4 or any(ch not in "0123456789abcdef" for ch in p):
            raise ValueError(f"grupo inválido: {p!r}")
        saida.append(int(p, 16))
    return saida


def parse_ipv6(texto: str) -> int:
    valor = 0
    for g in _grupos(texto):
        valor = (valor << 16) | g
    return valor


def _para_grupos(valor: int) -> list[int]:
    if not 0 <= valor < (1 << 128):
        raise ValueError("valor fora de 128 bits")
    return [(valor >> s) & 0xFFFF for s in range(112, -16, -16)]


def expandir(texto: str) -> str:
    """Forma completa: 8 grupos de 4 dígitos hexadecimais."""
    return ":".join(f"{g:04x}" for g in _grupos(texto))


def compactar_valor(valor: int) -> str:
    g = _para_grupos(valor)
    melhor_ini, melhor_len = -1, 0
    i = 0
    while i < 8:
        if g[i] == 0:
            j = i
            while j < 8 and g[j] == 0:
                j += 1
            if j - i > melhor_len:
                melhor_ini, melhor_len = i, j - i
            i = j
        else:
            i += 1
    if melhor_len < 2:  # RFC 5952: nunca comprimir um único grupo
        return ":".join(f"{x:x}" for x in g)
    esq = ":".join(f"{x:x}" for x in g[:melhor_ini])
    dir_ = ":".join(f"{x:x}" for x in g[melhor_ini + melhor_len:])
    return f"{esq}::{dir_}"


def compactar(texto: str) -> str:
    return compactar_valor(parse_ipv6(texto))


def eh_loopback(texto: str) -> bool:
    return parse_ipv6(texto) == 1


def eh_link_local(texto: str) -> bool:
    return parse_ipv6(texto) >> 118 == 0b1111111010  # fe80::/10
