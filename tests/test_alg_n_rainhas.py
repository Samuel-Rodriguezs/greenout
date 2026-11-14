import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from alg_n_rainhas import resolver_n_rainhas


def valida(sol: list[int]) -> bool:
    n = len(sol)
    for i in range(n):
        for j in range(i + 1, n):
            if sol[i] == sol[j] or abs(sol[i] - sol[j]) == j - i:
                return False
    return True


class TesteNRainhas(unittest.TestCase):
    def test_contagens_conhecidas(self):
        esperado = {0: 1, 1: 1, 2: 0, 3: 0, 4: 2, 5: 10, 6: 4, 8: 92}
        for n, qtd in esperado.items():
            self.assertEqual(len(resolver_n_rainhas(n)), qtd, f"n={n}")

    def test_solucoes_validas(self):
        for sol in resolver_n_rainhas(6):
            self.assertEqual(len(sol), 6)
            self.assertTrue(valida(sol))

    def test_quatro_rainhas(self):
        self.assertEqual(sorted(resolver_n_rainhas(4)), [[1, 3, 0, 2], [2, 0, 3, 1]])

    def test_negativo(self):
        with self.assertRaises(ValueError):
            resolver_n_rainhas(-1)


if __name__ == "__main__":
    unittest.main()
