import sys
import unittest
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from uni_factor import fatorar, main


class TestUniFactor(unittest.TestCase):
    def test_um(self):
        self.assertEqual(fatorar(1), [])

    def test_primo(self):
        self.assertEqual(fatorar(97), [97])
        self.assertEqual(fatorar(2), [2])

    def test_composto(self):
        self.assertEqual(fatorar(360), [2, 2, 2, 3, 3, 5])

    def test_potencia(self):
        self.assertEqual(fatorar(1024), [2] * 10)

    def test_grande(self):
        self.assertEqual(fatorar(600851475143), [71, 839, 1471, 6857])

    def test_produto_confere(self):
        n = 123456
        p = 1
        for f in fatorar(n):
            p *= f
        self.assertEqual(p, n)

    def test_invalido(self):
        for ruim in (0, -5):
            with self.assertRaises(ValueError):
                fatorar(ruim)

    def test_main_args(self):
        s = StringIO()
        self.assertEqual(main(["12", "7"], "", s), 0)
        self.assertEqual(s.getvalue(), "12: 2 2 3\n7: 7\n")

    def test_main_stdin_e_um(self):
        s = StringIO()
        main([], "1\n", s)
        self.assertEqual(s.getvalue(), "1:\n")

    def test_main_erro_continua(self):
        s = StringIO()
        self.assertEqual(main(["abc", "6"], "", s), 1)
        self.assertEqual(s.getvalue(), "6: 2 3\n")


if __name__ == "__main__":
    unittest.main()
