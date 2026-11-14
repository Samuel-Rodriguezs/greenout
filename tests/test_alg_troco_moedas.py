import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from alg_troco_moedas import troco_minimo


class TesteTrocoMoedas(unittest.TestCase):
    def test_exemplo_basico(self):
        self.assertEqual(troco_minimo([1, 2, 5], 11), 3)

    def test_guloso_falha(self):
        self.assertEqual(troco_minimo([1, 3, 4], 6), 2)

    def test_impossivel(self):
        self.assertEqual(troco_minimo([2], 3), -1)

    def test_valor_zero(self):
        self.assertEqual(troco_minimo([1, 2], 0), 0)

    def test_sem_moedas(self):
        self.assertEqual(troco_minimo([], 5), -1)
        self.assertEqual(troco_minimo([], 0), 0)

    def test_valor_negativo(self):
        with self.assertRaises(ValueError):
            troco_minimo([1], -1)

    def test_moeda_invalida(self):
        with self.assertRaises(ValueError):
            troco_minimo([0, 1], 3)

    def test_valor_grande(self):
        self.assertEqual(troco_minimo([1, 5, 10, 25, 50, 100], 289), 9)


if __name__ == "__main__":
    unittest.main()
