import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from proj_velha import novo_tabuleiro, vencedor, jogar, jogadas_validas, melhor_jogada


class TestVelha(unittest.TestCase):
    def test_vencedor_linha(self):
        t = novo_tabuleiro()
        for p in (0, 1, 2):
            t = jogar(t, p, "X")
        self.assertEqual(vencedor(t), "X")

    def test_sem_vencedor(self):
        self.assertIsNone(vencedor(novo_tabuleiro()))

    def test_jogada_invalida(self):
        t = jogar(novo_tabuleiro(), 4, "X")
        with self.assertRaises(ValueError):
            jogar(t, 4, "O")
        with self.assertRaises(ValueError):
            jogar(t, 9, "O")
        with self.assertRaises(ValueError):
            jogar(t, 0, "Z")

    def test_nao_muta_original(self):
        t = novo_tabuleiro()
        jogar(t, 0, "X")
        self.assertEqual(jogadas_validas(t), list(range(9)))

    def test_ia_vence_quando_pode(self):
        t = novo_tabuleiro()
        for p in (0, 1):
            t = jogar(t, p, "X")
        t = jogar(t, 3, "O")
        t = jogar(t, 4, "O")
        self.assertEqual(melhor_jogada(t, "X"), 2)

    def test_ia_bloqueia(self):
        t = novo_tabuleiro()
        t = jogar(t, 0, "X")
        t = jogar(t, 1, "X")
        t = jogar(t, 4, "O")
        self.assertEqual(melhor_jogada(t, "O"), 2)

    def test_ia_contra_ia_empata(self):
        t, vez = novo_tabuleiro(), "X"
        while vencedor(t) is None and jogadas_validas(t):
            t = jogar(t, melhor_jogada(t, vez), vez)
            vez = "O" if vez == "X" else "X"
        self.assertIsNone(vencedor(t))

    def test_jogo_encerrado(self):
        t = novo_tabuleiro()
        for p in (0, 1, 2):
            t = jogar(t, p, "X")
        with self.assertRaises(ValueError):
            melhor_jogada(t, "O")


if __name__ == "__main__":
    unittest.main()
