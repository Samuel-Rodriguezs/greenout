import sys
import unittest
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from uni_expand import desexpandir_linha, expandir_linha, main


class TestUniExpand(unittest.TestCase):
    def test_tab_inicial(self):
        self.assertEqual(expandir_linha("\ta", 4), "    a")

    def test_tab_alinha_coluna(self):
        self.assertEqual(expandir_linha("ab\tc", 4), "ab  c")

    def test_sem_tab(self):
        self.assertEqual(expandir_linha("abc"), "abc")

    def test_tab_invalido(self):
        with self.assertRaises(ValueError):
            expandir_linha("a", 0)
        with self.assertRaises(ValueError):
            desexpandir_linha("a", -1)

    def test_desexpandir(self):
        self.assertEqual(desexpandir_linha("        x", 4), "\t\tx")
        self.assertEqual(desexpandir_linha("      x", 4), "\t  x")

    def test_desexpandir_sem_espacos(self):
        self.assertEqual(desexpandir_linha("x  y", 4), "x  y")

    def test_ida_e_volta(self):
        l = "\t\tabc"
        self.assertEqual(desexpandir_linha(expandir_linha(l, 4), 4), l)

    def test_main(self):
        s = StringIO()
        self.assertEqual(main(["-t", "2"], "\tx\n", s), 0)
        self.assertEqual(s.getvalue(), "  x\n")
        s = StringIO()
        main(["-u", "-t", "2"], "    x\n", s)
        self.assertEqual(s.getvalue(), "\t\tx\n")

    def test_main_erros(self):
        self.assertEqual(main(["-t", "0"], "a\n", StringIO()), 2)
        self.assertEqual(main(["-t", "x"], "", StringIO()), 2)
        self.assertEqual(main(["-q"], "", StringIO()), 2)


if __name__ == "__main__":
    unittest.main()
