import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from mat_collatz import maior_passos_ate, passos, sequencia


class TestCollatz(unittest.TestCase):
    def test_sequencia(self):
        self.assertEqual(sequencia(6), [6, 3, 10, 5, 16, 8, 4, 2, 1])
        self.assertEqual(sequencia(1), [1])

    def test_passos(self):
        self.assertEqual(passos(1), 0)
        self.assertEqual(passos(27), 111)
        self.assertEqual(passos(16), 4)

    def test_maior_passos(self):
        self.assertEqual(maior_passos_ate(10), 9)
        self.assertEqual(maior_passos_ate(1000), 871)
        self.assertEqual(maior_passos_ate(1), 1)

    def test_invalido(self):
        with self.assertRaises(ValueError):
            sequencia(0)
        with self.assertRaises(ValueError):
            maior_passos_ate(0)


if __name__ == "__main__":
    unittest.main()
