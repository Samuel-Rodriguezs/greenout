import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fin_var import cvar_historico, quantil, var_historico, var_parametrico

R = [-0.05, -0.03, -0.01, 0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06]


class TestVaR(unittest.TestCase):
    def test_quantil(self):
        self.assertAlmostEqual(quantil([1, 2, 3, 4], 0.5), 2.5)
        self.assertEqual(quantil([3, 1, 2], 0.0), 1)
        self.assertEqual(quantil([3, 1, 2], 1.0), 3)

    def test_var_historico(self):
        self.assertAlmostEqual(var_historico(R, 0.9), 0.032)

    def test_cvar(self):
        self.assertAlmostEqual(cvar_historico(R, 0.9), 0.05)

    def test_cvar_maior_ou_igual_var(self):
        self.assertGreaterEqual(cvar_historico(R, 0.8), var_historico(R, 0.8))

    def test_var_parametrico(self):
        self.assertAlmostEqual(var_parametrico(0.0, 0.01, 0.95), 0.01644854, places=7)
        self.assertAlmostEqual(var_parametrico(0.001, 0.01, 0.99), 0.0232635 - 0.001, places=6)
        self.assertAlmostEqual(var_parametrico(0.0, 0.0), 0.0)

    def test_erros(self):
        with self.assertRaises(ValueError):
            var_historico([], 0.95)
        with self.assertRaises(ValueError):
            var_historico(R, 1.0)
        with self.assertRaises(ValueError):
            var_parametrico(0, -1)


if __name__ == "__main__":
    unittest.main()
