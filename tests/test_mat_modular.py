import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from mat_modular import inverso_modular, potencia_modular, teorema_chines


class TestModular(unittest.TestCase):
    def test_potencia(self):
        self.assertEqual(potencia_modular(2, 10, 1000), 24)
        self.assertEqual(potencia_modular(3, 0, 7), 1)
        self.assertEqual(potencia_modular(5, 3, 1), 0)
        self.assertEqual(potencia_modular(-2, 3, 7), pow(-2, 3, 7))
        self.assertEqual(potencia_modular(7, 10 ** 18, 10 ** 9 + 7), pow(7, 10 ** 18, 10 ** 9 + 7))

    def test_inverso(self):
        self.assertEqual(inverso_modular(3, 7), 5)
        for a in range(1, 13):
            self.assertEqual(a * inverso_modular(a, 13) % 13, 1)

    def test_sem_inverso(self):
        with self.assertRaises(ValueError):
            inverso_modular(4, 8)

    def test_chines(self):
        self.assertEqual(teorema_chines([2, 3, 2], [3, 5, 7]), 23)
        self.assertEqual(teorema_chines([1], [5]), 1)

    def test_erros(self):
        with self.assertRaises(ValueError):
            potencia_modular(2, 3, 0)
        with self.assertRaises(ValueError):
            potencia_modular(2, -1, 5)
        with self.assertRaises(ValueError):
            teorema_chines([1, 2], [4, 6])
        with self.assertRaises(ValueError):
            teorema_chines([], [])


if __name__ == "__main__":
    unittest.main()
