import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_minesweeper import contar_vizinhos


class TestKataMinesweeper(unittest.TestCase):
    def test_vazio(self):
        self.assertEqual(contar_vizinhos([]), [])

    def test_uma_celula(self):
        self.assertEqual(contar_vizinhos(["."]), ["0"])
        self.assertEqual(contar_vizinhos(["*"]), ["*"])

    def test_linha(self):
        self.assertEqual(contar_vizinhos(["*.."]), ["*10"])
        self.assertEqual(contar_vizinhos([".*."]), ["1*1"])

    def test_coluna(self):
        self.assertEqual(contar_vizinhos(["*", ".", "."]), ["*", "1", "0"])

    def test_diagonais(self):
        self.assertEqual(contar_vizinhos(["*.", ".."]), ["*1", "11"])

    def test_exemplo_classico(self):
        entrada = ["*...", "....", ".*..", "...."]
        esperado = ["*100", "2210", "1*10", "1110"]
        self.assertEqual(contar_vizinhos(entrada), esperado)

    def test_cercada(self):
        entrada = ["***", "*.*", "***"]
        self.assertEqual(contar_vizinhos(entrada), ["***", "*8*", "***"])

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            contar_vizinhos(["*.", "."])
        with self.assertRaises(ValueError):
            contar_vizinhos(["x"])


if __name__ == "__main__":
    unittest.main()
