import sys
import unittest
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from uni_cut import cortar, main, parse_campos


class TestUniCut(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(parse_campos("1,3-4"), [1, 3, 4])
        self.assertEqual(parse_campos("2,2"), [2])

    def test_parse_invalido(self):
        for ruim in ("0", "a", "3-1", "", "1,,2"):
            with self.assertRaises(ValueError):
                parse_campos(ruim)

    def test_cortar(self):
        self.assertEqual(cortar(["a:b:c"], [1, 3], ":"), ["a:c"])

    def test_campo_alem_do_fim(self):
        self.assertEqual(cortar(["a:b"], [2, 5], ":"), ["b"])

    def test_sem_delimitador(self):
        self.assertEqual(cortar(["abc"], [2], ":"), ["abc"])

    def test_campo_vazio(self):
        self.assertEqual(cortar(["a::c"], [2], ":"), [""])

    def test_main(self):
        s = StringIO()
        self.assertEqual(main(["-d", ",", "-f", "2"], "x,y\nz,w\n", s), 0)
        self.assertEqual(s.getvalue(), "y\nw\n")

    def test_main_tab_padrao(self):
        s = StringIO()
        main(["-f", "1"], "a\tb\n", s)
        self.assertEqual(s.getvalue(), "a\n")

    def test_main_erros(self):
        self.assertEqual(main([], "", StringIO()), 2)
        self.assertEqual(main(["-f", "x"], "", StringIO()), 2)
        self.assertEqual(main(["-d", "ab", "-f", "1"], "", StringIO()), 2)
        self.assertEqual(main(["-z"], "", StringIO()), 2)


if __name__ == "__main__":
    unittest.main()
