"""Conecta 4 com IA minimax (poda alfa-beta)."""
from __future__ import annotations

import random

LINHAS, COLUNAS = 6, 7


class Conecta4:
    def __init__(self) -> None:
        self.grade: list[list[int]] = [[0] * COLUNAS for _ in range(LINHAS)]
        self.vez = 1
        self.vencedor = 0

    def colunas_validas(self) -> list[int]:
        return [c for c in range(COLUNAS) if self.grade[0][c] == 0]

    @property
    def empate(self) -> bool:
        return not self.vencedor and not self.colunas_validas()

    @property
    def terminou(self) -> bool:
        return bool(self.vencedor) or self.empate

    def soltar(self, coluna: int) -> int:
        """Solta a peça do jogador da vez; retorna a linha onde caiu."""
        if self.terminou:
            raise RuntimeError("jogo terminado")
        if not 0 <= coluna < COLUNAS or self.grade[0][coluna]:
            raise ValueError("coluna inválida")
        l = max(i for i in range(LINHAS) if self.grade[i][coluna] == 0)
        self.grade[l][coluna] = self.vez
        if self._ganhou(l, coluna):
            self.vencedor = self.vez
        self.vez = 3 - self.vez
        return l

    def _desfazer(self, l: int, c: int) -> None:
        self.grade[l][c] = 0
        self.vez = 3 - self.vez
        self.vencedor = 0

    def _ganhou(self, l: int, c: int) -> bool:
        j = self.grade[l][c]
        for dl, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
            n = 1
            for s in (1, -1):
                a, b = l + dl * s, c + dc * s
                while 0 <= a < LINHAS and 0 <= b < COLUNAS and self.grade[a][b] == j:
                    n += 1
                    a, b = a + dl * s, b + dc * s
            if n >= 4:
                return True
        return False

    def _avaliar(self, jogador: int) -> int:
        """Heurística: centro vale mais; janelas de 4 com 3 peças e 1 vazio."""
        pontos = sum(3 for l in range(LINHAS) if self.grade[l][COLUNAS // 2] == jogador)
        pontos -= sum(3 for l in range(LINHAS) if self.grade[l][COLUNAS // 2] == 3 - jogador)
        for l in range(LINHAS):
            for c in range(COLUNAS):
                for dl, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                    fim_l, fim_c = l + 3 * dl, c + 3 * dc
                    if not (0 <= fim_l < LINHAS and 0 <= fim_c < COLUNAS):
                        continue
                    janela = [self.grade[l + i * dl][c + i * dc] for i in range(4)]
                    if janela.count(jogador) == 3 and janela.count(0) == 1:
                        pontos += 5
                    if janela.count(3 - jogador) == 3 and janela.count(0) == 1:
                        pontos -= 5
        return pontos

    def _minimax(self, prof: int, alfa: float, beta: float, jogador: int) -> float:
        if self.vencedor:
            return (1000 + prof) if self.vencedor == jogador else -(1000 + prof)
        if self.empate:
            return 0
        if prof == 0:
            return self._avaliar(jogador)
        maximizando = self.vez == jogador
        melhor = -1e9 if maximizando else 1e9
        for c in self._ordem():
            l = self.soltar(c)
            v = self._minimax(prof - 1, alfa, beta, jogador)
            self._desfazer(l, c)
            if maximizando:
                melhor = max(melhor, v)
                alfa = max(alfa, v)
            else:
                melhor = min(melhor, v)
                beta = min(beta, v)
            if alfa >= beta:
                break
        return melhor

    def _ordem(self) -> list[int]:
        return sorted(self.colunas_validas(), key=lambda c: abs(c - COLUNAS // 2))

    def melhor_jogada(self, profundidade: int = 4, rng: random.Random | None = None) -> int:
        """Escolhe a coluna da IA para o jogador da vez; desempates via rng."""
        if self.terminou:
            raise RuntimeError("jogo terminado")
        jogador = self.vez
        pontuacoes: dict[int, float] = {}
        for c in self.colunas_validas():
            l = self.soltar(c)
            pontuacoes[c] = self._minimax(profundidade - 1, -1e9, 1e9, jogador)
            self._desfazer(l, c)
        topo = max(pontuacoes.values())
        melhores = [c for c, v in pontuacoes.items() if v == topo]
        return (rng or random.Random(0)).choice(melhores)
