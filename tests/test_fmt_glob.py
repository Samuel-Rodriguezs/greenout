import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fmt_glob import ErroGlob, casa, filtrar


class TestFmtGlob(unittest.TestCase):
    def test_estrela_e_interrogacao(self):
        casos = [("*.py", "a.py", True), ("*.py", "a.pyc", False), ("a?c", "abc", True),
                 ("a?c", "ac", False), ("*", "", True), ("a*b*c", "aXXbYYc", True),
                 ("a*b*c", "aXXbYY", False), ("**", "xyz", True), ("*a", "bbb", False)]
        for p, t, esp in casos:
            with self.subTest(p=p, t=t):
                self.assertEqual(casa(p, t), esp)

    def test_classes(self):
        self.assertTrue(casa("[a-c]x", "bx"))
        self.assertFalse(casa("[a-c]x", "dx"))
        self.assertTrue(casa("[!a-c]x", "dx"))
        self.assertFalse(casa("[!a-c]x", "ax"))
        self.assertTrue(casa("[]a]x", "]x"))
        self.assertTrue(casa("[a-]x", "-x"))
        self.assertTrue(casa("file[0-9][0-9].txt", "file42.txt"))
        self.assertFalse(casa("file[0-9][0-9].txt", "file4.txt"))

    def test_escape(self):
        self.assertTrue(casa(r"a\*b", "a*b"))
        self.assertFalse(casa(r"a\*b", "aXb"))
        self.assertTrue(casa(r"[\]]", "]"))

    def test_caminho(self):
        self.assertFalse(casa("*.py", "src/a.py", caminho=True))
        self.assertTrue(casa("src/*.py", "src/a.py", caminho=True))
        self.assertFalse(casa("src/*.py", "src/x/a.py", caminho=True))
        self.assertTrue(casa("src/**/*.py", "src/x/y/a.py", caminho=True))
        self.assertTrue(casa("src/**/*.py", "src/a.py", caminho=True))
        self.assertFalse(casa("a?b", "a/b", caminho=True))
        self.assertTrue(casa("*.py", "src/a.py", caminho=False))

    def test_filtrar(self):
        self.assertEqual(filtrar("*.md", ["a.md", "b.txt", "c.md"]), ["a.md", "c.md"])

    def test_padrao_patologico_rapido(self):
        self.assertFalse(casa("a*a*a*a*a*a*a*a*b", "a" * 60))

    def test_malformados(self):
        for ruim in ["[abc", "[z-a]", "a[", "[!"]:
            with self.subTest(ruim=ruim):
                with self.assertRaises(ErroGlob):
                    casa(ruim, "abc")


if __name__ == "__main__":
    unittest.main()
