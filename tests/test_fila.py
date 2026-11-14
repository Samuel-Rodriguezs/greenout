import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fila import Fila


class TestFila(unittest.TestCase):
    def test_fifo(self):
        f = Fila()
        f.enfileirar("a")
        f.enfileirar("b")
        self.assertEqual(f.desenfileirar(), "a")
        self.assertEqual(len(f), 1)

    def test_vazia(self):
        with self.assertRaises(IndexError):
            Fila().desenfileirar()


if __name__ == "__main__":
    unittest.main()
