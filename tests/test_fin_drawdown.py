import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fin_drawdown import drawdown_maximo, serie_drawdown


class TestDrawdown(unittest.TestCase):
    def test_serie(self):
        s = serie_drawdown([100, 120, 90, 110])
        for a, b in zip(s, [0, 0, -0.25, -1 / 12]):
            self.assertAlmostEqual(a, b)

    def test_maximo_com_recuperacao(self):
        r = drawdown_maximo([100, 120, 90, 110, 80, 130])
        self.assertAlmostEqual(r.valor, 80 / 120 - 1)
        self.assertEqual((r.indice_pico, r.indice_vale, r.indice_recuperacao), (1, 4, 5))

    def test_sem_recuperacao(self):
        r = drawdown_maximo([100, 50, 60])
        self.assertAlmostEqual(r.valor, -0.5)
        self.assertIsNone(r.indice_recuperacao)

    def test_so_alta(self):
        r = drawdown_maximo([1, 2, 3])
        self.assertEqual(r.valor, 0.0)

    def test_erros(self):
        with self.assertRaises(ValueError):
            drawdown_maximo([])
        with self.assertRaises(ValueError):
            serie_drawdown([1, 0])


if __name__ == "__main__":
    unittest.main()
