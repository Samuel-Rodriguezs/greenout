"""Jogo da Vida de Conway sobre conjunto de celulas vivas (grade infinita)."""
from collections import Counter
from typing import FrozenSet, Iterable, Tuple

Celula = Tuple[int, int]


def proxima_geracao(vivas: Iterable[Celula]) -> FrozenSet[Celula]:
    vivas = frozenset(vivas)
    contagem: Counter = Counter()
    for (x, y) in vivas:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    contagem[(x + dx, y + dy)] += 1
    return frozenset(c for c, n in contagem.items() if n == 3 or (n == 2 and c in vivas))


def simular(vivas: Iterable[Celula], geracoes: int) -> FrozenSet[Celula]:
    if geracoes < 0:
        raise ValueError("geracoes negativas")
    atual = frozenset(vivas)
    for _ in range(geracoes):
        atual = proxima_geracao(atual)
    return atual


def de_texto(texto: str) -> FrozenSet[Celula]:
    return frozenset(
        (x, y)
        for y, linha in enumerate(texto.strip("\n").splitlines())
        for x, ch in enumerate(linha)
        if ch == "#"
    )


def para_texto(vivas: Iterable[Celula]) -> str:
    vivas = frozenset(vivas)
    if not vivas:
        return ""
    xs = [c[0] for c in vivas]
    ys = [c[1] for c in vivas]
    return "\n".join(
        "".join("#" if (x, y) in vivas else "." for x in range(min(xs), max(xs) + 1))
        for y in range(min(ys), max(ys) + 1)
    )
