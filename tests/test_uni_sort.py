import sys
import unittest
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from uni_sort import main, ordenar


class TestUniSort(unittest.TestCase):
    def test_lexicografico(self):
        self.assertEqual(ordenar(["b", "a", "10", "9"]), ["10", "9", "a", "b"])

    def test_numerico(self):
        self.assertEqual(ordenar(["10", "9", "-1", "2.5"], numerico=True),
                         ["-1", "2.5", "9", "10"])

    def test_reverso(self):
        self.assertEqual(ordenar(["a", "c", "b"], reverso=True), ["c", "b", "a"])

    def test_unico(self):
        self.assertEqual(ordenar(["b", "a", "b", "a"], unico=True), ["a", "b"])

    def test_unico_numerico(self):
        self.assertEqual(ordenar(["1", "1.0", "2"], numerico=True, unico=True), ["1", "2"])

    def test_vazio(self):
        self.assertEqual(ordenar([]), [])

    def test_nao_numerico_vale_zero(self):
        self.assertEqual(ordenar(["x", "-3", "5"], numerico=True), ["-3", "x", "5"])

    def test_main(self):
        s = StringIO()
        self.assertEqual(main(["-nr"], "1\n3\n2\n", s), 0)
        self.assertEqual(s.getvalue(), "3\n2\n1\n")

    def test_main_opcao_invalida(self):
        self.assertEqual(main(["-q"], "", StringIO()), 2)

    def test_main_arquivo_inexistente(self):
        self.assertEqual(main(["/nao/existe/xyz"], "", StringIO()), 2)


if __name__ == "__main__":
    unittest.main()
