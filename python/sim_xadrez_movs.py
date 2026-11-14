"""Xadrez reduzido: apenas movimentos de cavalo e torre."""
from __future__ import annotations

Casa = tuple[int, int]  # (coluna 0-7 = a-h, linha 0-7 = 1-8)

SALTOS_CAVALO = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]
DIRECOES_TORRE = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def casa_de_nome(nome: str) -> Casa:
    if len(nome) != 2 or nome[0] not in "abcdefgh" or nome[1] not in "12345678":
        raise ValueError(f"casa inválida: {nome!r}")
    return ord(nome[0]) - 97, int(nome[1]) - 1


def nome_da_casa(casa: Casa) -> str:
    return chr(97 + casa[0]) + str(casa[1] + 1)


def _dentro(c: int, l: int) -> bool:
    return 0 <= c < 8 and 0 <= l < 8


class Tabuleiro:
    """Peças: dict casa -> (cor, tipo), com cor 'B'/'P' e tipo 'C' (cavalo) ou 'T' (torre)."""

    def __init__(self, pecas: dict[Casa, tuple[str, str]] | None = None) -> None:
        self.pecas: dict[Casa, tuple[str, str]] = dict(pecas or {})

    def movimentos(self, origem: Casa) -> list[Casa]:
        if origem not in self.pecas:
            raise ValueError("sem peça na casa")
        cor, tipo = self.pecas[origem]
        c0, l0 = origem
        destinos: list[Casa] = []
        if tipo == "C":
            for dc, dl in SALTOS_CAVALO:
                c, l = c0 + dc, l0 + dl
                if _dentro(c, l) and self.pecas.get((c, l), (None,))[0] != cor:
                    destinos.append((c, l))
        elif tipo == "T":
            for dc, dl in DIRECOES_TORRE:
                c, l = c0 + dc, l0 + dl
                while _dentro(c, l):
                    alvo = self.pecas.get((c, l))
                    if alvo is None:
                        destinos.append((c, l))
                    else:
                        if alvo[0] != cor:
                            destinos.append((c, l))
                        break
                    c, l = c + dc, l + dl
        else:
            raise ValueError("tipo de peça desconhecido")
        return sorted(destinos)

    def mover(self, origem: Casa, destino: Casa) -> tuple[str, str] | None:
        """Move a peça; retorna a peça capturada (se houver)."""
        if destino not in self.movimentos(origem):
            raise ValueError("movimento ilegal")
        capturada = self.pecas.pop(destino, None)
        self.pecas[destino] = self.pecas.pop(origem)
        return capturada


def menor_caminho_cavalo(origem: Casa, destino: Casa) -> int:
    """Número mínimo de saltos do cavalo em tabuleiro vazio (BFS)."""
    from collections import deque

    fila = deque([(origem, 0)])
    visto = {origem}
    while fila:
        (c, l), d = fila.popleft()
        if (c, l) == destino:
            return d
        for dc, dl in SALTOS_CAVALO:
            n = (c + dc, l + dl)
            if _dentro(*n) and n not in visto:
                visto.add(n)
                fila.append((n, d + 1))
    raise ValueError("destino inalcançável")
