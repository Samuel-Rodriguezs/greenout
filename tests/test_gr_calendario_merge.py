import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_calendario_merge import horarios_livres, inserir, mesclar, tem_conflito


class TestCalendario(unittest.TestCase):
    def test_mesclar(self):
        self.assertEqual(mesclar([(8, 10), (1, 3), (2, 6), (15, 18), (17, 20)]), [(1, 6), (8, 10), (15, 20)])

    def test_adjacentes_e_contidos(self):
        self.assertEqual(mesclar([(1, 4), (4, 5)]), [(1, 5)])
        self.assertEqual(mesclar([(1, 10), (2, 3)]), [(1, 10)])

    def test_vazio_e_invertido(self):
        self.assertEqual(mesclar([]), [])
        with self.assertRaises(ValueError):
            mesclar([(5, 1)])

    def test_livres(self):
        self.assertEqual(horarios_livres([(9, 10), (13, 15), (14, 16)], 8, 18), [(8, 9), (10, 13), (16, 18)])

    def test_livres_bordas(self):
        self.assertEqual(horarios_livres([], 8, 18), [(8, 18)])
        self.assertEqual(horarios_livres([(0, 20)], 8, 18), [])
        self.assertEqual(horarios_livres([(6, 9), (19, 22)], 8, 18), [(9, 18)])
        with self.assertRaises(ValueError):
            horarios_livres([], 10, 9)

    def test_conflito(self):
        self.assertTrue(tem_conflito([(1, 5), (4, 8)]))
        self.assertFalse(tem_conflito([(1, 5), (5, 8)]))
        self.assertFalse(tem_conflito([]))

    def test_inserir(self):
        self.assertEqual(inserir([(1, 2), (5, 6)], (2, 5)), [(1, 6)])
        self.assertEqual(inserir([(1, 2)], (8, 9)), [(1, 2), (8, 9)])


if __name__ == "__main__":
    unittest.main()
