import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ml_metricas import (acuracia, f1, matriz_confusao, mse, precisao, r2,
                         revocacao, roc_auc)

Y = [1, 1, 1, 0, 0, 0, 0, 1]
P = [1, 0, 1, 0, 1, 0, 0, 1]


class TestMetricas(unittest.TestCase):
    def test_confusao(self):
        self.assertEqual(matriz_confusao(Y, P), (3, 1, 1, 3))

    def test_basicas(self):
        self.assertEqual(acuracia(Y, P), 0.75)
        self.assertEqual(precisao(Y, P), 0.75)
        self.assertEqual(revocacao(Y, P), 0.75)
        self.assertAlmostEqual(f1(Y, P), 0.75)

    def test_sem_positivos_previstos(self):
        self.assertEqual(precisao([1, 0], [0, 0]), 0.0)
        self.assertEqual(f1([1, 0], [0, 0]), 0.0)
        self.assertEqual(revocacao([0, 0], [0, 0]), 0.0)

    def test_auc_perfeito_e_inverso(self):
        self.assertEqual(roc_auc([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]), 1.0)
        self.assertEqual(roc_auc([0, 0, 1, 1], [0.9, 0.8, 0.2, 0.1]), 0.0)

    def test_auc_empates_e_classico(self):
        self.assertEqual(roc_auc([0, 1], [0.5, 0.5]), 0.5)
        self.assertAlmostEqual(roc_auc([0, 0, 1, 1], [0.1, 0.4, 0.35, 0.8]), 0.75)

    def test_auc_uma_classe(self):
        with self.assertRaises(ValueError):
            roc_auc([1, 1], [0.1, 0.2])

    def test_mse_r2(self):
        self.assertEqual(mse([1, 2, 3], [1, 2, 5]), 4 / 3)
        self.assertEqual(r2([1, 2, 3], [1, 2, 3]), 1.0)
        self.assertEqual(r2([1, 2, 3], [2, 2, 2]), 0.0)
        self.assertLess(r2([1, 2, 3], [3, 2, 1]), 0)

    def test_r2_constante(self):
        self.assertEqual(r2([2, 2], [2, 2]), 1.0)
        self.assertEqual(r2([2, 2], [1, 3]), 0.0)

    def test_tamanhos_invalidos(self):
        with self.assertRaises(ValueError):
            acuracia([1], [1, 0])
        with self.assertRaises(ValueError):
            mse([], [])


if __name__ == "__main__":
    unittest.main()
