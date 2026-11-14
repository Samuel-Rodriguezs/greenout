import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from mat_fatoracao import divisores, fatorar, fatorar_expoentes, totiente


class TestFatoracao(unittest.TestCase):
    def test_fatorar(self):
        self.assertEqual(fatorar(1), [])
        self.assertEqual(fatorar(2), [2])
        self.assertEqual(fatorar(360), [2, 2, 2, 3, 3, 5])
        self.assertEqual(fatorar(97), [97])

    def test_produto_confere(self):
        for n in (123456, 999983, 2 ** 10 * 3 ** 4):
            p = 1
            for f in fatorar(n):
                p *= f
            self.assertEqual(p, n)

    def test_expoentes(self):
        self.assertEqual(fatorar_expoentes(360), {2: 3, 3: 2, 5: 1})

    def test_divisores(self):
        self.assertEqual(divisores(12), [1, 2, 3, 4, 6, 12])
        self.assertEqual(divisores(1), [1])
        self.assertEqual(divisores(36)[-1], 36)

    def test_totiente(self):
        self.assertEqual(totiente(1), 1)
        self.assertEqual(totiente(9), 6)
        self.assertEqual(totiente(36), 12)
        self.assertEqual(totiente(97), 96)

    def test_invalido(self):
        with self.assertRaises(ValueError):
            fatorar(0)
        with self.assertRaises(ValueError):
            divisores(-4)


if __name__ == "__main__":
    unittest.main()
