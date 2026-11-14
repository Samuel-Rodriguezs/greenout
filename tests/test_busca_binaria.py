import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from busca_binaria import busca_binaria


class TestBusca(unittest.TestCase):
    def test_achou(self):
        self.assertEqual(busca_binaria([1, 3, 5, 7, 9], 7), 3)

    def test_nao_achou(self):
        self.assertEqual(busca_binaria([1, 3, 5], 4), -1)
        self.assertEqual(busca_binaria([], 1), -1)


if __name__ == "__main__":
    unittest.main()
