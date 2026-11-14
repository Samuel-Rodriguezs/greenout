import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_payback import payback


class TestDomPayback(unittest.TestCase):
    def test_simples(self):
        self.assertEqual(payback([-1000, 400, 400, 400]), Decimal("2.5"))

    def test_exato(self):
        self.assertEqual(payback([-1000, 500, 500]), Decimal("2"))

    def test_nunca_recupera(self):
        self.assertIsNone(payback([-1000, 100, 100]))

    def test_descontado_maior_que_simples(self):
        simples = payback([-1000, 600, 600])
        desc = payback([-1000, 600, 600], "0.10")
        self.assertEqual(simples, Decimal(1) + Decimal(400) / 600)
        self.assertGreater(desc, simples)
        # 600/1.1 = 545.4545...; faltam 454.5454...; 600/1.21 = 495.8677...
        self.assertAlmostEqual(float(desc), 1 + 454.545454 / 495.867769, places=5)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            payback([])
        with self.assertRaises(ValueError):
            payback([-1, 2], "-0.1")


if __name__ == "__main__":
    unittest.main()
