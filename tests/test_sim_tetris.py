import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sim_tetris import FORMAS, Tetris, rotacionar


class TestTetris(unittest.TestCase):
    def test_rotacao_quatro_vezes_identidade(self):
        for forma in FORMAS.values():
            r = forma
            for _ in range(4):
                r = rotacionar(r)
            self.assertEqual(r, forma)

    def test_rotacao_i(self):
        self.assertEqual(rotacionar(FORMAS["I"]), frozenset({(0, 0), (1, 0), (2, 0), (3, 0)}))

    def test_o_invariante(self):
        self.assertEqual(rotacionar(FORMAS["O"]), FORMAS["O"])

    def test_paredes(self):
        t = Tetris(rng=random.Random(1))
        t._nova_peca("O")
        while t.mover(0, -1):
            pass
        self.assertEqual(min(c for _, c in t.celulas_peca()), 0)
        self.assertFalse(t.mover(0, -1))

    def test_queda_e_chao(self):
        t = Tetris(rng=random.Random(1))
        t._nova_peca("O")
        t.queda_livre()
        self.assertTrue(t.tabuleiro[19][4])
        self.assertTrue(t.tabuleiro[18][5])

    def test_limpar_linhas(self):
        t = Tetris(4, 4, random.Random(1))
        t.tabuleiro[3] = ["X", "X", "", ""]
        t.tabuleiro[2] = ["X", "", "", ""]
        t._nova_peca("O")
        t.pos = (2, 2)
        n = t._travar()
        self.assertEqual(n, 1)
        self.assertEqual(t.pontos, 100)
        self.assertEqual(t.tabuleiro[3], ["X", "", "O", "O"])

    def test_rotacao_bloqueada_por_parede_usa_kick(self):
        t = Tetris(rng=random.Random(1))
        t._nova_peca("I")
        t.rotacionar()
        while t.mover(0, 1):
            pass
        self.assertTrue(t.rotacionar())

    def test_fim_de_jogo(self):
        t = Tetris(4, 4, random.Random(2))
        for _ in range(10):
            t.queda_livre()
        self.assertTrue(t.fim)
        self.assertFalse(t.mover(1, 0))

    def test_determinismo(self):
        a, b = Tetris(rng=random.Random(4)), Tetris(rng=random.Random(4))
        self.assertEqual(a.nome, b.nome)


if __name__ == "__main__":
    unittest.main()
