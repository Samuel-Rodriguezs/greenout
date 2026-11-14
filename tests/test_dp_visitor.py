import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_visitor import Avaliador, ContadorNos, Impressor, Numero, Produto, Soma

# (2 + 3) * 4
ARVORE = Produto(Soma(Numero(2), Numero(3)), Numero(4))


class TestVisitor(unittest.TestCase):
    def test_avaliar(self):
        self.assertEqual(ARVORE.aceitar(Avaliador()), 20)

    def test_imprimir(self):
        self.assertEqual(ARVORE.aceitar(Impressor()), "(2 + 3) * 4")

    def test_contar(self):
        self.assertEqual(ARVORE.aceitar(ContadorNos()), 5)

    def test_folha(self):
        self.assertEqual(Numero(1.5).aceitar(Impressor()), "1.5")


if __name__ == "__main__":
    unittest.main()
