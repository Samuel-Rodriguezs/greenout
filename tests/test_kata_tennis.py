import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_tennis import Jogo, placar


class TestKataTennis(unittest.TestCase):
    def test_empates_iniciais(self):
        self.assertEqual(placar(0, 0), "Love-All")
        self.assertEqual(placar(1, 1), "Fifteen-All")
        self.assertEqual(placar(2, 2), "Thirty-All")

    def test_deuce(self):
        self.assertEqual(placar(3, 3), "Deuce")
        self.assertEqual(placar(5, 5), "Deuce")

    def test_placares_normais(self):
        self.assertEqual(placar(1, 0), "Fifteen-Love")
        self.assertEqual(placar(0, 3), "Love-Forty")
        self.assertEqual(placar(3, 2), "Forty-Thirty")

    def test_vantagem(self):
        self.assertEqual(placar(4, 3), "Advantage A")
        self.assertEqual(placar(3, 4), "Advantage B")
        self.assertEqual(placar(7, 6), "Advantage A")

    def test_vitoria(self):
        self.assertEqual(placar(4, 0), "Win for A")
        self.assertEqual(placar(1, 4), "Win for B")
        self.assertEqual(placar(8, 6), "Win for A")

    def test_negativo(self):
        with self.assertRaises(ValueError):
            placar(-1, 0)

    def test_jogo_completo(self):
        j = Jogo()
        for p in "AABBBA":
            j.ponto(p)
        self.assertEqual(j.placar(), "Deuce")
        j.ponto("B")
        self.assertEqual(j.placar(), "Advantage B")
        j.ponto("B")
        self.assertTrue(j.terminou())
        self.assertEqual(j.placar(), "Win for B")

    def test_jogo_terminado_rejeita_ponto(self):
        j = Jogo()
        for _ in range(4):
            j.ponto("A")
        with self.assertRaises(ValueError):
            j.ponto("B")
        with self.assertRaises(ValueError):
            Jogo().ponto("C")


if __name__ == "__main__":
    unittest.main()
