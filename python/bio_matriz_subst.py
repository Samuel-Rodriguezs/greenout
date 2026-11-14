"""Matriz de substituição simples para DNA (transições x transversões)."""

PURINAS = frozenset("AG")
PIRIMIDINAS = frozenset("CT")


def classificar(a: str, b: str) -> str:
    """'identidade', 'transicao' (A<->G, C<->T) ou 'transversao'."""
    if len(a) != 1 or len(b) != 1 or a not in "ACGT" or b not in "ACGT":
        raise ValueError("bases devem ser A, C, G ou T")
    if a == b:
        return "identidade"
    if ({a, b} <= PURINAS) or ({a, b} <= PIRIMIDINAS):
        return "transicao"
    return "transversao"


def matriz(
    match: int = 2, transicao: int = -1, transversao: int = -2
) -> dict[tuple[str, str], int]:
    valores = {"identidade": match, "transicao": transicao, "transversao": transversao}
    return {(a, b): valores[classificar(a, b)] for a in "ACGT" for b in "ACGT"}


def pontuar(a: str, b: str, m: dict[tuple[str, str], int] | None = None) -> int:
    """Soma da pontuação coluna a coluna de duas sequências sem gaps."""
    if len(a) != len(b):
        raise ValueError("tamanhos diferentes")
    m = m or matriz()
    return sum(m[(x, y)] for x, y in zip(a, b))


def contar_ts_tv(a: str, b: str) -> tuple[int, int]:
    """(transições, transversões) entre duas sequências de mesmo tamanho."""
    if len(a) != len(b):
        raise ValueError("tamanhos diferentes")
    tipos = [classificar(x, y) for x, y in zip(a, b)]
    return tipos.count("transicao"), tipos.count("transversao")
