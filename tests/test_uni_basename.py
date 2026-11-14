import sys
import unittest
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from uni_basename import basename, dirname, main


class TestUniBasename(unittest.TestCase):
    def test_basename(self):
        self.assertEqual(basename("/usr/bin/python"), "python")
        self.assertEqual(basename("arquivo.txt"), "arquivo.txt")

    def test_basename_barra_final(self):
        self.assertEqual(basename("/a/b/"), "b")

    def test_basename_raiz_e_vazio(self):
        self.assertEqual(basename("/"), "/")
        self.assertEqual(basename("//"), "/")
        self.assertEqual(basename(""), "")

    def test_basename_sufixo(self):
        self.assertEqual(basename("/a/foo.txt", ".txt"), "foo")
        self.assertEqual(basename("/a/foo.txt", ".md"), "foo.txt")
        self.assertEqual(basename("/a/.txt", ".txt"), ".txt")

    def test_dirname(self):
        self.assertEqual(dirname("/usr/bin/python"), "/usr/bin")
        self.assertEqual(dirname("/a/b/"), "/a")

    def test_dirname_bordas(self):
        self.assertEqual(dirname("arquivo"), ".")
        self.assertEqual(dirname("/arquivo"), "/")
        self.assertEqual(dirname("/"), "/")
        self.assertEqual(dirname(""), ".")
        self.assertEqual(dirname("a//b"), "a")

    def test_main(self):
        s = StringIO()
        self.assertEqual(main(["basename", "/x/y.c", ".c"], "", s), 0)
        self.assertEqual(s.getvalue(), "y\n")
        s = StringIO()
        self.assertEqual(main(["dirname", "/x/y.c"], "", s), 0)
        self.assertEqual(s.getvalue(), "/x\n")

    def test_main_erros(self):
        self.assertEqual(main([], "", StringIO()), 2)
        self.assertEqual(main(["foo", "x"], "", StringIO()), 2)
        self.assertEqual(main(["basename"], "", StringIO()), 2)
        self.assertEqual(main(["basename", "a", "b", "c"], "", StringIO()), 2)
        self.assertEqual(main(["dirname", "a", "b"], "", StringIO()), 2)


if __name__ == "__main__":
    unittest.main()
