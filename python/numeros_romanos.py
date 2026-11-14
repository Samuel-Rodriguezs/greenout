"""Conversão entre inteiros (1 a 3999) e números romanos."""

_TABELA = [
    (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
    (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
]


def inteiro_para_romano(n: int) -> str:
    """Converte inteiro de 1 a 3999 em romano; ValueError fora do intervalo."""
    if not 1 <= n <= 3999:
        raise ValueError("número deve estar entre 1 e 3999")
    partes = []
    for valor, simbolo in _TABELA:
        while n >= valor:
            partes.append(simbolo)
            n -= valor
    return "".join(partes)


def romano_para_inteiro(romano: str) -> int:
    """Converte romano em inteiro; ValueError se a escrita não for canônica."""
    if not romano:
        raise ValueError("romano vazio")
    posicao, total = 0, 0
    for valor, simbolo in _TABELA:
        while romano.startswith(simbolo, posicao):
            total += valor
            posicao += len(simbolo)
    if posicao != len(romano) or inteiro_para_romano(total) != romano:
        raise ValueError(f"romano inválido: {romano!r}")
    return total
