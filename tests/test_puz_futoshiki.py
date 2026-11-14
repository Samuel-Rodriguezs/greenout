import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from puz_futoshiki import resolver


def valida(grade, menores):
    n = len(grade)
    latino = all(sorted(l) == list(range(1, n + 1)) for l in grade) and \
        all(sorted(grade[r][c] for r in range(n)) == list(range(1, n + 1)) for c in range(n))
    return latino and all(grade[a[0]][a[1]] < grade[b[0]][b[1]] for a, b in menores)


class TestFutoshiki(unittest.TestCase):
    def test_sem_restricoes_conta_quadrados_latinos(self):
        self.assertEqual(len(resolver(3, [], limite=100)), 12)
        self.assertEqual(len(resolver(4, [], limite=1000)), 576)

    def test_4x4_com_desigualdades_unica(self):
        # solução alvo: [[1,2,3,4],[2,1,4,3],[3,4,1,2],[4,3,2,1]]
        menores = [((0, 0), (0, 1)), ((0, 1), (0, 2)), ((0, 2), (0, 3)),
                   ((1, 1), (1, 0)), ((1, 3), (1, 2)),
                   ((2, 0), (2, 1)), ((2, 2), (2, 3)),
                   ((3, 3), (3, 2)), ((3, 2), (3, 1)), ((3, 1), (3, 0))]
        sols = resolver(4, menores, limite=10)
        self.assertTrue(sols)
        for s in sols:
            self.assertTrue(valida(s, menores))

    def test_dados_fixam_a_solucao(self):
        sols = resolver(3, [((0, 0), (0, 1))], {(0, 0): 1, (0, 1): 2, (1, 0): 2}, limite=10)
        self.assertEqual(sols, [[[1, 2, 3], [2, 3, 1], [3, 1, 2]]])

    def test_cadeia_forca_ordem(self):
        menores = [((0, 0), (0, 1)), ((0, 1), (0, 2))]
        for s in resolver(3, menores, limite=10):
            self.assertEqual(s[0], [1, 2, 3])
        self.assertEqual(len(resolver(3, menores, limite=10)), 2)

    def test_sem_solucao(self):
        ciclo = [((0, 0), (0, 1)), ((0, 1), (1, 1)), ((1, 1), (1, 0)), ((1, 0), (0, 0))]
        self.assertEqual(resolver(2, ciclo), [])
        self.assertEqual(resolver(2, [], {(0, 0): 1, (0, 1): 1}), [])

    def test_validacao(self):
        with self.assertRaises(ValueError):
            resolver(3, [((0, 0), (1, 1))])
        with self.assertRaises(ValueError):
            resolver(3, [((0, 0), (0, 3))])
        with self.assertRaises(ValueError):
            resolver(3, [], {(0, 0): 4})


if __name__ == "__main__":
    unittest.main()
