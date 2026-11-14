"""Janela deslizante, blocos e agrupamento de execuções consecutivas."""
import itertools
from collections import deque
from typing import Iterable, Iterator, List, Tuple, TypeVar

T = TypeVar("T")


def janela_deslizante(itens: Iterable[T], tamanho: int) -> Iterator[Tuple[T, ...]]:
    if tamanho < 1:
        raise ValueError("tamanho deve ser >= 1")
    janela: deque = deque(maxlen=tamanho)
    for item in itens:
        janela.append(item)
        if len(janela) == tamanho:
            yield tuple(janela)


def blocos(itens: Iterable[T], tamanho: int) -> Iterator[List[T]]:
    if tamanho < 1:
        raise ValueError("tamanho deve ser >= 1")
    it = iter(itens)
    while bloco := list(itertools.islice(it, tamanho)):
        yield bloco


def execucoes(itens: Iterable[T]) -> List[Tuple[T, int]]:
    """Compressão por execuções: 'aabccc' -> [('a',2),('b',1),('c',3)]."""
    return [(k, sum(1 for _ in g)) for k, g in itertools.groupby(itens)]
