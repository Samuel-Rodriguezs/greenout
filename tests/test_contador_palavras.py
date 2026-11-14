import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from contador_palavras import contar_palavras


class TestContador(unittest.TestCase):
    def test_contagem(self):
        c = contar_palavras("O gato e o rato. O gato fugiu!")
        self.assertEqual(c["o"], 3)
        self.assertEqual(c["gato"], 2)
        self.assertEqual(c["fugiu"], 1)


if __name__ == "__main__":
    unittest.main()
