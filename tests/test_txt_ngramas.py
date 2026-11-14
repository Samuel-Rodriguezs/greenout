import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from txt_ngramas import contar_ngramas, ngramas, ngramas_caracteres


class TestNgramas(unittest.TestCase):
    def test_bigramas(self):
        self.assertEqual(ngramas(["a", "b", "c"], 2), [("a", "b"), ("b", "c")])

    def test_n_maior_que_tamanho(self):
        self.assertEqual(ngramas(["a"], 3), [])
        self.assertEqual(ngramas([], 1), [])

    def test_n_invalido(self):
        with self.assertRaises(ValueError):
            ngramas([1, 2], 0)

    def test_caracteres(self):
        self.assertEqual(ngramas_caracteres("casa", 2), ["ca", "as", "sa"])

    def test_contar(self):
        c = contar_ngramas("abab", 2)
        self.assertEqual(c[("a", "b")], 2)
        self.assertEqual(c[("b", "a")], 1)


if __name__ == "__main__":
    unittest.main()
