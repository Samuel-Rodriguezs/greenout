import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ml_divisao_dados import k_fold, k_fold_estratificado, train_test_split


class TestDivisao(unittest.TestCase):
    def test_tamanhos_e_particao(self):
        X = list(range(20))
        y = [v * 10 for v in X]
        Xtr, Xte, ytr, yte = train_test_split(X, y, 0.25, seed=1)
        self.assertEqual((len(Xtr), len(Xte)), (15, 5))
        self.assertEqual(sorted(Xtr + Xte), X)
        self.assertEqual(ytr, [v * 10 for v in Xtr])
        self.assertEqual(yte, [v * 10 for v in Xte])

    def test_seed(self):
        X = list(range(30))
        a = train_test_split(X, X, seed=3)
        self.assertEqual(a, train_test_split(X, X, seed=3))
        self.assertNotEqual(a[1], train_test_split(X, X, seed=4)[1])

    def test_sem_embaralhar(self):
        _, Xte, _, _ = train_test_split(list(range(10)), list(range(10)), 0.2, embaralhar=False)
        self.assertEqual(Xte, [0, 1])

    def test_invalidos_split(self):
        with self.assertRaises(ValueError):
            train_test_split([1, 2], [1])
        with self.assertRaises(ValueError):
            train_test_split([1, 2], [1, 2], 1.0)
        with self.assertRaises(ValueError):
            train_test_split([1], [1], 0.5)

    def test_kfold_cobre_tudo_uma_vez(self):
        vistos = []
        for treino, val in k_fold(23, 5, seed=1):
            self.assertEqual(set(treino) & set(val), set())
            self.assertEqual(len(treino) + len(val), 23)
            vistos += val
        self.assertEqual(sorted(vistos), list(range(23)))

    def test_kfold_tamanhos_balanceados(self):
        tams = [len(v) for _, v in k_fold(23, 5)]
        self.assertEqual(sorted(tams), [4, 4, 5, 5, 5])

    def test_kfold_leave_one_out(self):
        self.assertEqual(len(list(k_fold(4, 4))), 4)

    def test_kfold_invalido(self):
        with self.assertRaises(ValueError):
            list(k_fold(5, 1))
        with self.assertRaises(ValueError):
            list(k_fold(3, 4))

    def test_estratificado(self):
        y = ["a"] * 10 + ["b"] * 5
        for treino, val in k_fold_estratificado(y, 5, seed=2):
            self.assertEqual(sum(y[i] == "b" for i in val), 1)
            self.assertEqual(len(treino) + len(val), 15)


if __name__ == "__main__":
    unittest.main()
