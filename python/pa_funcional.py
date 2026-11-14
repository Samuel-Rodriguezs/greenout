"""functools: composição, aplicação parcial, redução e memoização com lru_cache."""
import functools
from typing import Callable, Iterable


def compor(*funcoes: Callable) -> Callable:
    """compor(f, g, h)(x) == f(g(h(x))). Sem funções, devolve identidade."""
    if not funcoes:
        return lambda x: x
    return functools.reduce(lambda f, g: lambda *a, **k: f(g(*a, **k)), funcoes)


def aplicar_parcial(funcao: Callable, *args, **kwargs) -> Callable:
    return functools.partial(funcao, *args, **kwargs)


def produto(numeros: Iterable[float]) -> float:
    return functools.reduce(lambda a, b: a * b, numeros, 1)


@functools.lru_cache(maxsize=None)
def caminhos_grade(linhas: int, colunas: int) -> int:
    """Nº de caminhos (direita/baixo) do canto superior esquerdo ao inferior direito."""
    if linhas < 1 or colunas < 1:
        raise ValueError("dimensões devem ser >= 1")
    if linhas == 1 or colunas == 1:
        return 1
    return caminhos_grade(linhas - 1, colunas) + caminhos_grade(linhas, colunas - 1)
