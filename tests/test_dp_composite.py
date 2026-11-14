import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_composite import Arquivo, Diretorio


class TestComposite(unittest.TestCase):
    def setUp(self):
        self.raiz = Diretorio("raiz").adicionar(
            Arquivo("a.txt", 10),
            Diretorio("sub").adicionar(Arquivo("b.txt", 5), Arquivo("c.txt", 7)),
            Diretorio("vazio"),
        )

    def test_tamanho_recursivo(self):
        self.assertEqual(self.raiz.tamanho(), 22)
        self.assertEqual(Diretorio("vazio").tamanho(), 0)

    def test_listagem(self):
        self.assertEqual(list(self.raiz.listar()), [
            "raiz/", "raiz/a.txt", "raiz/sub/", "raiz/sub/b.txt",
            "raiz/sub/c.txt", "raiz/vazio/"])

    def test_folha(self):
        self.assertEqual(Arquivo("x", 3).tamanho(), 3)


if __name__ == "__main__":
    unittest.main()
