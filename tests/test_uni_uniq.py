import sys
import unittest
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from uni_uniq import agrupar, main, uniq


class TestUniUniq(unittest.TestCase):
    def test_agrupar(self):
        self.assertEqual(agrupar(["a", "a", "b", "a"]), [("a", 2), ("b", 1), ("a", 1)])

    def test_vazio(self):
        self.assertEqual(uniq([]), [])

    def test_somente_adjacentes(self):
        self.assertEqual(uniq(["a", "b", "a"]), ["a", "b", "a"])

    def test_remove_repetidas(self):
        self.assertEqual(uniq(["a", "a", "b"]), ["a", "b"])

    def test_contagem(self):
        self.assertEqual(uniq(["a", "a", "b"], contar=True), ["      2 a", "      1 b"])

    def test_duplicadas(self):
        self.assertEqual(uniq(["a", "a", "b", "c", "c", "c"], duplicadas=True), ["a", "c"])

    def test_main(self):
        s = StringIO()
        self.assertEqual(main(["-d"], "x\nx\ny\n", s), 0)
        self.assertEqual(s.getvalue(), "x\n")

    def test_main_argumento_invalido(self):
        self.assertEqual(main(["-z"], "", StringIO()), 2)


if __name__ == "__main__":
    unittest.main()
