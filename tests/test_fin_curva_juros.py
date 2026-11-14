import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fin_curva_juros import CurvaJuros


class TestCurvaJuros(unittest.TestCase):
    def setUp(self):
        self.c = CurvaJuros([3, 1], [0.12, 0.10])  # desordenado de propósito

    def test_linear(self):
        self.assertAlmostEqual(self.c.taxa_linear(2), 0.11)
        self.assertAlmostEqual(self.c.taxa_linear(1), 0.10)
        self.assertAlmostEqual(self.c.taxa_linear(1.5), 0.105)

    def test_extrapolacao_plana(self):
        self.assertEqual(self.c.taxa_linear(0.25), 0.10)
        self.assertEqual(self.c.taxa_linear(10), 0.12)

    def test_flat_forward(self):
        esperado = (1.1 * 1.12**3) ** 0.5
        self.assertAlmostEqual(self.c.taxa_flat_forward(2), esperado**0.5 - 1)

    def test_fator_desconto(self):
        self.assertAlmostEqual(self.c.fator_desconto(1), 1 / 1.1)
        self.assertAlmostEqual(self.c.fator_desconto(3), 1 / 1.12**3)

    def test_forward(self):
        self.assertAlmostEqual(self.c.taxa_forward(1, 2), 1.11**2 / 1.10 - 1)

    def test_forward_em_curva_plana(self):
        plana = CurvaJuros([1, 5], [0.08, 0.08])
        self.assertAlmostEqual(plana.taxa_forward(1, 4), 0.08)
        self.assertAlmostEqual(plana.taxa_forward(1, 4, "flat"), 0.08)

    def test_um_vertice(self):
        self.assertEqual(CurvaJuros([2], [0.09]).taxa_linear(7), 0.09)

    def test_erros(self):
        with self.assertRaises(ValueError):
            CurvaJuros([], [])
        with self.assertRaises(ValueError):
            CurvaJuros([1, 1], [0.1, 0.2])
        with self.assertRaises(ValueError):
            CurvaJuros([0], [0.1])
        with self.assertRaises(ValueError):
            self.c.taxa_linear(0)
        with self.assertRaises(ValueError):
            self.c.taxa_forward(2, 1)


if __name__ == "__main__":
    unittest.main()
