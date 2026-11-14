import itertools
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from alg_permutacoes import permutacoes, subconjuntos


class TestePermutacoes(unittest.TestCase):
    def test_vazia(self):
        self.assertEqual(permutacoes([]), [[]])

    def test_um_elemento(self):
        self.assertEqual(permutacoes([1]), [[1]])

    def test_tres_elementos(self):
        self.assertEqual(
            permutacoes([1, 2, 3]),
            [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]],
        )

    def test_igual_itertools(self):
        esperado = [list(p) for p in itertools.permutations("abcd")]
        self.assertEqual(permutacoes(list("abcd")), esperado)

    def test_nao_altera_entrada(self):
        entrada = [3, 1, 2]
        permutacoes(entrada)
        self.assertEqual(entrada, [3, 1, 2])


class TesteSubconjuntos(unittest.TestCase):
    def test_vazio(self):
        self.assertEqual(subconjuntos([]), [[]])

    def test_tres_elementos(self):
        self.assertEqual(
            sorted(subconjuntos([1, 2, 3])),
            [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]],
        )

    def test_quantidade(self):
        self.assertEqual(len(subconjuntos(list(range(8)))), 256)


if __name__ == "__main__":
    unittest.main()
