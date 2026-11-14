import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ds_matriz_confusao import matriz_confusao

REAIS = [1, 1, 1, 0, 0, 0, 0, 1]
PREV = [1, 0, 1, 0, 0, 1, 0, 1]


class TestMatrizConfusao(unittest.TestCase):
    def test_binaria(self):
        m = matriz_confusao(REAIS, PREV)
        self.assertEqual(m.rotulos, [0, 1])
        self.assertEqual(m.matriz, [[3, 1], [1, 3]])
        self.assertEqual((m.vp(1), m.fp(1), m.fn(1), m.vn(1)), (3, 1, 1, 3))
        self.assertAlmostEqual(m.acuracia(), 0.75)
        self.assertAlmostEqual(m.precisao(1), 0.75)
        self.assertAlmostEqual(m.revocacao(1), 0.75)
        self.assertAlmostEqual(m.f1(1), 0.75)
        # po = 0.75, pe = (4*4 + 4*4)/64 = 0.5 -> kappa = 0.5
        self.assertAlmostEqual(m.kappa(), 0.5)

    def test_multiclasse(self):
        reais = ["a", "a", "b", "b", "c", "c", "c"]
        prev = ["a", "b", "b", "b", "c", "a", "c"]
        m = matriz_confusao(reais, prev)
        self.assertEqual(m.matriz, [[1, 1, 0], [0, 2, 0], [1, 0, 2]])
        self.assertAlmostEqual(m.precisao("a"), 0.5)
        self.assertAlmostEqual(m.precisao("b"), 2 / 3)
        self.assertAlmostEqual(m.revocacao("c"), 2 / 3)
        self.assertAlmostEqual(m.revocacao("b"), 1.0)
        self.assertAlmostEqual(m.acuracia(), 5 / 7)
        f_a = 2 * 0.5 * 0.5 / 1.0
        f_b = 2 * (2 / 3) * 1.0 / (2 / 3 + 1.0)
        f_c = 2 * 1.0 * (2 / 3) / (1.0 + 2 / 3)
        self.assertAlmostEqual(m.f1_macro(), (f_a + f_b + f_c) / 3)

    def test_rotulos_explicitos_e_sem_previsao(self):
        m = matriz_confusao([1, 1], [1, 1], rotulos=[0, 1])
        self.assertEqual(m.precisao(0), 0.0)
        self.assertEqual(m.f1(0), 0.0)
        self.assertAlmostEqual(m.kappa(), 1.0)

    def test_formatar(self):
        txt = matriz_confusao(REAIS, PREV).formatar()
        self.assertEqual(len(txt.splitlines()), 3)

    def test_erros(self):
        with self.assertRaises(ValueError):
            matriz_confusao([1], [1, 2])
        with self.assertRaises(ValueError):
            matriz_confusao([1, 2], [1, 3], rotulos=[1, 2])


if __name__ == "__main__":
    unittest.main()
