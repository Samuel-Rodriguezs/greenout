"""Conversão de números entre bases arbitrárias (2 a 36)."""

_DIGITOS = "0123456789abcdefghijklmnopqrstuvwxyz"


def _validar_base(b: int) -> None:
    if not 2 <= b <= 36:
        raise ValueError("base deve estar entre 2 e 36")


def para_base(n: int, base: int) -> str:
    _validar_base(base)
    if n == 0:
        return "0"
    sinal = "-" if n < 0 else ""
    n = abs(n)
    ds = []
    while n:
        n, r = divmod(n, base)
        ds.append(_DIGITOS[r])
    return sinal + "".join(reversed(ds))


def de_base(texto: str, base: int) -> int:
    _validar_base(base)
    t = texto.strip().lower()
    sinal = -1 if t.startswith("-") else 1
    t = t.lstrip("+-")
    if not t:
        raise ValueError("texto vazio")
    v = 0
    for ch in t:
        d = _DIGITOS.find(ch)
        if d < 0 or d >= base:
            raise ValueError(f"dígito inválido para base {base}: {ch!r}")
        v = v * base + d
    return sinal * v


def converter(texto: str, base_origem: int, base_destino: int) -> str:
    return para_base(de_base(texto, base_origem), base_destino)
