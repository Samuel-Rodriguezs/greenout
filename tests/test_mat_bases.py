import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from mat_bases import converter, de_base, para_base


class TestBases(unittest.TestCase):
    def test_para_base(self):
        self.assertEqual(para_base(255, 2), "11111111")
        self.assertEqual(para_base(255, 16), "ff")
        self.assertEqual(para_base(0, 7), "0")
        self.assertEqual(para_base(-10, 2), "-1010")
        self.assertEqual(para_base(35, 36), "z")

    def test_de_base(self):
        self.assertEqual(de_base("ff", 16), 255)
        self.assertEqual(de_base("FF", 16), 255)
        self.assertEqual(de_base("-1010", 2), -10)
        self.assertEqual(de_base("z", 36), 35)

    def test_ida_e_volta(self):
        for base in range(2, 37):
            for n in (0, 1, 7, 12345, -999):
                self.assertEqual(de_base(para_base(n, base), base), n)

    def test_converter(self):
        self.assertEqual(converter("1010", 2, 16), "a")
        self.assertEqual(converter("777", 8, 10), "511")

    def test_erros(self):
        with self.assertRaises(ValueError):
            para_base(5, 1)
        with self.assertRaises(ValueError):
            para_base(5, 37)
        with self.assertRaises(ValueError):
            de_base("12", 2)
        with self.assertRaises(ValueError):
            de_base("", 10)
        with self.assertRaises(ValueError):
            de_base("-", 10)


if __name__ == "__main__":
    unittest.main()
