import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ds_ranking import ranking, top_n

DADOS = [10, 20, 20, 30]


class TestRanking(unittest.TestCase):
    def test_metodos(self):
        self.assertEqual(ranking(DADOS), [1, 2.5, 2.5, 4])
        self.assertEqual(ranking(DADOS, "minimo"), [1, 2, 2, 4])
        self.assertEqual(ranking(DADOS, "maximo"), [1, 3, 3, 4])
        self.assertEqual(ranking(DADOS, "denso"), [1, 2, 2, 3])
        self.assertEqual(ranking(DADOS, "ordinal"), [1, 2, 3, 4])

    def test_decrescente(self):
        self.assertEqual(ranking(DADOS, "minimo", decrescente=True), [4, 2, 2, 1])
        self.assertEqual(ranking(DADOS, "denso", decrescente=True), [3, 2, 2, 1])
        self.assertEqual(ranking([5, 1, 5], "ordinal", decrescente=True), [1, 3, 2])

    def test_nao_ordenado(self):
        self.assertEqual(ranking([3, 1, 2]), [3, 1, 2])
        self.assertEqual(ranking([]), [])

    def test_top_n(self):
        itens = [("ana", 90), ("bia", 90), ("caio", 80), ("duda", 70)]
        self.assertEqual(
            top_n(itens, 3), [(1, "ana", 90), (1, "bia", 90), (3, "caio", 80)]
        )
        self.assertEqual(top_n(itens, 0), [])

    def test_erros(self):
        with self.assertRaises(ValueError):
            ranking([1], "x")
        with self.assertRaises(ValueError):
            top_n([], -1)


if __name__ == "__main__":
    unittest.main()
