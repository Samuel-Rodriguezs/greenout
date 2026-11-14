import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fibonacci import fibonacci


class TestFibonacci(unittest.TestCase):
    def test_dez(self):
        self.assertEqual(fibonacci(10), [0, 1, 1, 2, 3, 5, 8, 13, 21, 34])

    def test_vazio(self):
        self.assertEqual(fibonacci(0), [])

    def test_negativo(self):
        with self.assertRaises(ValueError):
            fibonacci(-1)


if __name__ == "__main__":
    unittest.main()
