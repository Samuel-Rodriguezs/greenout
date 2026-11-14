import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import ds_amostragem as a


def media(v):
    return sum(v) / len(v)


class TestAmostragem(unittest.TestCase):
    def test_simples(self):
        dados = list(range(100))
        s = a.amostra_simples(dados, 10, seed=1)
        self.assertEqual(len(s), 10)
        self.assertEqual(len(set(s)), 10)
        self.assertTrue(set(s) <= set(dados))
        self.assertEqual(s, a.amostra_simples(dados, 10, seed=1))
        self.assertEqual(sorted(a.amostra_simples(dados, 100, seed=2)), dados)

    def test_com_reposicao(self):
        s = a.amostra_com_reposicao([1, 2], 50, seed=3)
        self.assertEqual(len(s), 50)
        self.assertEqual(set(s), {1, 2})
        self.assertEqual(s, a.amostra_com_reposicao([1, 2], 50, seed=3))

    def test_estratificada(self):
        regs = [{"g": "A", "i": i} for i in range(10)] + [{"g": "B", "i": i} for i in range(20)]
        s = a.amostra_estratificada(regs, "g", 0.5, seed=7)
        self.assertEqual(sum(1 for r in s if r["g"] == "A"), 5)
        self.assertEqual(sum(1 for r in s if r["g"] == "B"), 10)
        self.assertEqual(s, a.amostra_estratificada(regs, "g", 0.5, seed=7))

    def test_bootstrap_constante(self):
        self.assertEqual(set(a.bootstrap([5, 5, 5], media, 20, seed=1)), {5.0})
        self.assertEqual(a.ic_bootstrap([5, 5, 5], media, seed=1), (5.0, 5.0))

    def test_bootstrap_reprodutivel_e_limites(self):
        dados = [1, 2, 3, 4, 5, 6, 7, 8]
        b1 = a.bootstrap(dados, media, 200, seed=42)
        self.assertEqual(b1, a.bootstrap(dados, media, 200, seed=42))
        self.assertTrue(all(1 <= v <= 8 for v in b1))
        self.assertAlmostEqual(sum(b1) / len(b1), 4.5, delta=0.3)
        lo, hi = a.ic_bootstrap(dados, media, 0.95, 500, seed=42)
        self.assertLess(lo, 4.5)
        self.assertGreater(hi, 4.5)

    def test_erros(self):
        with self.assertRaises(ValueError):
            a.amostra_simples([1, 2], 3)
        with self.assertRaises(ValueError):
            a.amostra_com_reposicao([], 1)
        with self.assertRaises(ValueError):
            a.amostra_estratificada([{"g": 1}], "g", 0)
        with self.assertRaises(ValueError):
            a.bootstrap([], media)
        with self.assertRaises(ValueError):
            a.ic_bootstrap([1, 2], media, 1.5)


if __name__ == "__main__":
    unittest.main()
