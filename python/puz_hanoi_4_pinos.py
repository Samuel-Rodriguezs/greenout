"""Torre de Hanói generalizada para k pinos: movimentos ótimos de Frame-Stewart."""
from __future__ import annotations

from functools import lru_cache
from typing import Optional


@lru_cache(maxsize=None)
def frame_stewart(n: int, pinos: int) -> Optional[int]:
    """Menor número de movimentos de Frame-Stewart para n discos; None se impossível."""
    if n < 0 or pinos < 1:
        raise ValueError("parâmetros inválidos")
    if n == 0:
        return 0
    if pinos < 2 or (pinos == 2 and n > 1):
        return None
    if n == 1:
        return 1
    if pinos == 2:
        return None
    if pinos == 3:
        return 2 ** n - 1
    return min(2 * frame_stewart(k, pinos) + frame_stewart(n - k, pinos - 1) for k in range(1, n))


def melhor_k(n: int, pinos: int) -> int:
    """Quantidade de discos menores levados ao pino auxiliar na primeira fase."""
    return min(range(1, n), key=lambda k: (2 * frame_stewart(k, pinos) + frame_stewart(n - k, pinos - 1), k))


def resolver(n: int, pinos: int = 4) -> list[tuple[int, int, int]]:
    """Lista de movimentos (disco, origem, destino); pinos de 0 a pinos-1, disco 1 = menor.

    Levanta ValueError se não houver solução.
    """
    if frame_stewart(n, pinos) is None:
        raise ValueError("sem solução com essa quantidade de pinos")
    movimentos: list[tuple[int, int, int]] = []

    def mover(base: int, qtd: int, origem: int, destino: int, livres: list[int]) -> None:
        """Move os discos base+1..base+qtd (topo da pilha de `origem`)."""
        if qtd == 0:
            return
        if qtd == 1:
            movimentos.append((base + 1, origem, destino))
            return
        if len(livres) == 1:
            aux = livres[0]
            mover(base, qtd - 1, origem, aux, [destino])
            movimentos.append((base + qtd, origem, destino))
            mover(base, qtd - 1, aux, destino, [origem])
            return
        k = melhor_k(qtd, len(livres) + 2)
        aux, resto = livres[0], livres[1:]
        mover(base, k, origem, aux, [destino] + resto)           # k menores -> auxiliar
        mover(base + k, qtd - k, origem, destino, resto)          # maiores com um pino a menos
        mover(base, k, aux, destino, [origem] + resto)            # k menores -> destino

    mover(0, n, 0, pinos - 1, list(range(1, pinos - 1)))
    return movimentos


def simular(n: int, pinos: int, movimentos: list[tuple[int, int, int]]) -> list[list[int]]:
    """Executa os movimentos validando as regras e devolve o estado final dos pinos."""
    estado: list[list[int]] = [[] for _ in range(pinos)]
    estado[0] = list(range(n, 0, -1))
    for disco, o, d in movimentos:
        if not estado[o] or estado[o][-1] != disco:
            raise ValueError("disco não está no topo da origem")
        if estado[d] and estado[d][-1] < disco:
            raise ValueError("disco maior sobre menor")
        estado[d].append(estado[o].pop())
    return estado
