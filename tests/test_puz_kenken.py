import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from puz_kenken import contar_solucoes, resolver, satisfaz

# KenKen 4x4: as gaiolas abaixo foram derivadas da solução conhecida.
SOLUCAO = [[1, 2, 3, 4], [3, 4, 1, 2], [4, 3, 2, 1], [2, 1, 4, 3]]
GAIOLAS = [
    (((0, 0), (0, 1)), "-", 1),
    (((0, 2), (0, 3)), "+", 7),
    (((1, 0), (2, 0)), "+", 7),
    (((1, 1), (1, 2)), "*", 4),
    (((1, 3), (2, 3)), "-", 1),
    (((2, 1), (2, 2)), "*", 6),
    (((3, 0), (3, 1)), "/", 2),
    (((3, 2), (3, 3)), "+", 7),
]


class TestKenKen(unittest.TestCase):
    def test_satisfaz(self):
        self.assertTrue(satisfaz([5], "=", 5))
        self.assertTrue(satisfaz([2, 3], "+", 5))
        self.assertTrue(satisfaz([2, 3, 4], "*", 24))
        self.assertTrue(satisfaz([5, 2], "-", 3))
        self.assertTrue(satisfaz([2, 6], "/", 3))
        self.assertFalse(satisfaz([2, 5], "/", 2))
        self.assertFalse(satisfaz([1, 2, 3], "-", 1))
        with self.assertRaises(ValueError):
            satisfaz([1], "^", 1)

    def test_resolve_e_confere_gaiolas(self):
        sol = resolver(4, GAIOLAS)
        self.assertIsNotNone(sol)
        for linha in sol:
            self.assertEqual(sorted(linha), [1, 2, 3, 4])
        for c in range(4):
            self.assertEqual(sorted(sol[r][c] for r in range(4)), [1, 2, 3, 4])
        for cels, op, alvo in GAIOLAS:
            self.assertTrue(satisfaz([sol[r][c] for r, c in cels], op, alvo))

    def test_unico_com_dicas_travadas(self):
        # 3x3 todo com gaiolas de uma célula tem solução única
        sol3 = [[1, 2, 3], [2, 3, 1], [3, 1, 2]]
        gaiolas = [(((r, c),), "=", sol3[r][c]) for r in range(3) for c in range(3)]
        self.assertEqual(resolver(3, gaiolas), sol3)
        self.assertEqual(contar_solucoes(3, gaiolas), 1)

    def test_varias_solucoes_3x3(self):
        # só somas por linha: 12 quadrados latinos de ordem 3
        gaiolas = [(tuple((r, c) for c in range(3)), "+", 6) for r in range(3)]
        self.assertEqual(contar_solucoes(3, gaiolas, limite=100), 12)

    def test_sem_solucao(self):
        gaiolas = [(((0, 0), (0, 1)), "+", 2), (((1, 0), (1, 1)), "+", 3)]
        self.assertIsNone(resolver(2, gaiolas))  # 1+1 repete na linha
        gaiolas = [(((0, 0),), "=", 1), (((0, 1),), "=", 2), (((1, 0),), "=", 1), (((1, 1),), "=", 2)]
        self.assertIsNone(resolver(2, gaiolas))  # coluna repete 1

    def test_validacao(self):
        with self.assertRaises(ValueError):
            resolver(2, [(((0, 0), (0, 1)), "+", 3)])  # não cobre
        with self.assertRaises(ValueError):
            resolver(2, [(((0, 0), (0, 1), (1, 0)), "-", 1), (((1, 1),), "=", 1)])
        with self.assertRaises(ValueError):
            resolver(1, [(((0, 0),), "%", 1)])


if __name__ == "__main__":
    unittest.main()
