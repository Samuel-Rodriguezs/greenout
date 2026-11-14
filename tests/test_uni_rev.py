import sys
import unittest
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from uni_rev import inverter_linhas, main


class TestUniRev(unittest.TestCase):
    def test_inverter(self):
        self.assertEqual(inverter_linhas(["abc", "xy"]), ["cba", "yx"])

    def test_vazio(self):
        self.assertEqual(inverter_linhas([]), [])
        self.assertEqual(inverter_linhas([""]), [""])

    def test_palindromo(self):
        self.assertEqual(inverter_linhas(["arara"]), ["arara"])

    def test_acentos(self):
        self.assertEqual(inverter_linhas(["ação"]), ["oãça"])

    def test_main(self):
        s = StringIO()
        self.assertEqual(main([], "ab\ncd\n", s), 0)
        self.assertEqual(s.getvalue(), "ba\ndc\n")

    def test_main_argumento(self):
        self.assertEqual(main(["x"], "", StringIO()), 2)


if __name__ == "__main__":
    unittest.main()
