import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fin_titulo_preco import (
    duration_macaulay,
    duration_modificada,
    preco_titulo,
    ytm_por_preco,
)


class TestTitulo(unittest.TestCase):
    def test_ao_par(self):
        self.assertAlmostEqual(preco_titulo(1000, 0.05, 0.05, 3), 1000.0)

    def test_desconto_e_premio(self):
        self.assertAlmostEqual(preco_titulo(1000, 0.05, 0.06, 3), 973.2699, places=3)
        self.assertGreater(preco_titulo(1000, 0.05, 0.04, 3), 1000)

    def test_zero_cupom(self):
        self.assertAlmostEqual(preco_titulo(1000, 0.0, 0.10, 2), 1000 / 1.21)

    def test_duration(self):
        self.assertAlmostEqual(duration_macaulay(1000, 0.0, 0.1, 5), 5.0)
        self.assertAlmostEqual(duration_macaulay(1000, 0.05, 0.05, 3), 2.8594, places=3)
        self.assertAlmostEqual(duration_modificada(1000, 0.0, 0.1, 5), 5 / 1.1)

    def test_ytm_inverte_preco(self):
        p = preco_titulo(1000, 0.08, 0.0725, 10)
        self.assertAlmostEqual(ytm_por_preco(p, 1000, 0.08, 10), 0.0725, places=9)

    def test_ytm_zero_cupom(self):
        self.assertAlmostEqual(ytm_por_preco(826.446281, 1000, 0.0, 2), 0.10, places=6)

    def test_erros(self):
        with self.assertRaises(ValueError):
            preco_titulo(0, 0.05, 0.05, 3)
        with self.assertRaises(ValueError):
            preco_titulo(1000, 0.05, -1.0, 3)
        with self.assertRaises(ValueError):
            preco_titulo(1000, 0.05, 0.05, 0)
        with self.assertRaises(ValueError):
            ytm_por_preco(-5, 1000, 0.05, 3)


if __name__ == "__main__":
    unittest.main()
