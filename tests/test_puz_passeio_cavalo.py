import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from puz_passeio_cavalo import (SALTOS, passeio_backtracking,
                                passeio_warnsdorff, valido)


class TestPasseioCavalo(unittest.TestCase):
    def test_warnsdorff_8x8(self):
        caminho = passeio_warnsdorff(8)
        self.assertIsNotNone(caminho)
        self.assertTrue(valido(caminho, 8))

    def test_warnsdorff_5x5_de_varios_inicios(self):
        for inicio in [(0, 0), (2, 2), (4, 4)]:
            c = passeio_warnsdorff(5, inicio)
            if c is not None:
                self.assertTrue(valido(c, 5))
                self.assertEqual(c[0], inicio)

    def test_1x1(self):
        self.assertEqual(passeio_warnsdorff(1), [(0, 0)])

    def test_sem_solucao_tabuleiro_pequeno(self):
        self.assertIsNone(passeio_backtracking(3))
        self.assertIsNone(passeio_backtracking(4))
        self.assertIsNone(passeio_warnsdorff(2))

    def test_fechado_8x8(self):
        c = passeio_backtracking(8, fechado=True)
        self.assertIsNotNone(c)
        self.assertTrue(valido(c, 8))
        self.assertIn((c[0][0] - c[-1][0], c[0][1] - c[-1][1]), SALTOS)

    def test_fechado_impossivel_5x5(self):
        # tabuleiros de lado ímpar não admitem passeio fechado
        self.assertIsNone(passeio_backtracking(5, fechado=True))

    def test_inicio_invalido(self):
        with self.assertRaises(ValueError):
            passeio_warnsdorff(5, (5, 0))


if __name__ == "__main__":
    unittest.main()
