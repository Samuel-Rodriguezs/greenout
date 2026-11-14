import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from puz_nonograma import arranjos, contar_solucoes, pistas_de, resolver


class TestNonograma(unittest.TestCase):
    def test_arranjos(self):
        self.assertEqual(arranjos((2,), 3, (-1, -1, -1)), [(1, 1, 0), (0, 1, 1)])
        self.assertEqual(arranjos((1, 1), 3, (-1, -1, -1)), [(1, 0, 1)])
        self.assertEqual(arranjos((3,), 3, (0, -1, -1)), [])

    def test_resolve_coracao(self):
        alvo = [[0, 1, 0, 1, 0], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [0, 1, 1, 1, 0], [0, 0, 1, 0, 0]]
        linhas, colunas = pistas_de(alvo)
        self.assertEqual(resolver(linhas, colunas), alvo)

    def test_pistas_de(self):
        self.assertEqual(pistas_de([[1, 0, 1], [1, 1, 1]]), ([[1, 1], [3]], [[2], [1], [2]]))

    def test_sem_solucao(self):
        self.assertIsNone(resolver([[2], [0]], [[1], [0]]))  # somas diferentes
        self.assertIsNone(resolver([[2], [2]], [[1], [1], [2]]))  # soma ok, mas contraditório

    def test_ambiguo(self):
        # diagonal vs anti-diagonal: duas soluções
        self.assertEqual(contar_solucoes([[1], [1]], [[1], [1]]), 2)
        grade = resolver([[1], [1]], [[1], [1]])
        self.assertIn(grade, ([[1, 0], [0, 1]], [[0, 1], [1, 0]]))

    def test_unica(self):
        self.assertEqual(contar_solucoes([[2], [2]], [[2], [2]]), 1)


if __name__ == "__main__":
    unittest.main()
