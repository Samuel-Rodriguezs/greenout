"""Conversão entre decimal e binário sem usar bin()/int(base)."""


def decimal_para_binario(n: int) -> str:
    """Converte inteiro para string binária; suporta zero e negativos (prefixo '-')."""
    if n == 0:
        return "0"
    sinal = "-" if n < 0 else ""
    n = abs(n)
    digitos = []
    while n:
        digitos.append(str(n % 2))
        n //= 2
    return sinal + "".join(reversed(digitos))


def binario_para_decimal(binario: str) -> int:
    """Converte string binária (com '-' opcional) para inteiro; ValueError se inválida."""
    sinal = -1 if binario.startswith("-") else 1
    corpo = binario[1:] if binario.startswith("-") else binario
    if not corpo or any(c not in "01" for c in corpo):
        raise ValueError(f"binário inválido: {binario!r}")
    valor = 0
    for c in corpo:
        valor = valor * 2 + int(c)
    return sinal * valor
