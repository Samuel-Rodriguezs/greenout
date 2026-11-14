"""Damas simples (8x8) com captura obrigatória e promoção."""
from __future__ import annotations

Pos = tuple[int, int]
Peca = str  # 'b','B' (brancas/dama) e 'p','P' (pretas/dama)


class Damas:
    def __init__(self) -> None:
        self.tab: dict[Pos, Peca] = {}
        for l in range(8):
            for c in range(8):
                if (l + c) % 2 == 1:
                    if l < 3:
                        self.tab[(l, c)] = "p"
                    elif l > 4:
                        self.tab[(l, c)] = "b"
        self.vez = "b"

    @staticmethod
    def _cor(p: Peca) -> str:
        return p.lower()

    def _direcoes(self, p: Peca) -> list[Pos]:
        if p.isupper():
            return [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        return [(-1, -1), (-1, 1)] if p == "b" else [(1, -1), (1, 1)]

    @staticmethod
    def _dentro(l: int, c: int) -> bool:
        return 0 <= l < 8 and 0 <= c < 8

    def capturas(self, origem: Pos) -> list[tuple[Pos, Pos]]:
        """Lista (destino, peça_capturada) para saltos simples."""
        p = self.tab[origem]
        res = []
        for dl, dc in self._direcoes(p):
            meio = (origem[0] + dl, origem[1] + dc)
            fim = (origem[0] + 2 * dl, origem[1] + 2 * dc)
            if self._dentro(*fim) and meio in self.tab and \
                    self._cor(self.tab[meio]) != self._cor(p) and fim not in self.tab:
                res.append((fim, meio))
        return res

    def simples(self, origem: Pos) -> list[Pos]:
        p = self.tab[origem]
        return [(origem[0] + dl, origem[1] + dc) for dl, dc in self._direcoes(p)
                if self._dentro(origem[0] + dl, origem[1] + dc) and (origem[0] + dl, origem[1] + dc) not in self.tab]

    def _ha_captura(self, cor: str) -> bool:
        return any(self._cor(p) == cor and self.capturas(pos) for pos, p in self.tab.items())

    def jogadas_legais(self) -> list[tuple[Pos, Pos]]:
        obrigatoria = self._ha_captura(self.vez)
        res = []
        for pos, p in sorted(self.tab.items()):
            if self._cor(p) != self.vez:
                continue
            if obrigatoria:
                res += [(pos, d) for d, _ in self.capturas(pos)]
            else:
                res += [(pos, d) for d in self.simples(pos)]
        return res

    def mover(self, origem: Pos, destino: Pos) -> bool:
        """Executa a jogada. Retorna True se o mesmo jogador deve continuar capturando."""
        if (origem, destino) not in self.jogadas_legais():
            raise ValueError("jogada ilegal")
        p = self.tab.pop(origem)
        capturou = abs(destino[0] - origem[0]) == 2
        if capturou:
            del self.tab[((origem[0] + destino[0]) // 2, (origem[1] + destino[1]) // 2)]
        promovida = (p == "b" and destino[0] == 0) or (p == "p" and destino[0] == 7)
        self.tab[destino] = p.upper() if promovida else p
        if capturou and not promovida and self.capturas(destino):
            self._continuacao = destino
            return True
        self.vez = "p" if self.vez == "b" else "b"
        return False

    @property
    def vencedor(self) -> str | None:
        for cor in ("b", "p"):
            if not any(self._cor(p) == cor for p in self.tab.values()):
                return "p" if cor == "b" else "b"
        return None
