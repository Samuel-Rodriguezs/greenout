import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_memento import Carrinho, Zelador


class TestMemento(unittest.TestCase):
    def test_restaurar(self):
        c = Carrinho()
        c.adicionar("pao", 2)
        snap = c.salvar()
        c.adicionar("leite")
        c.cupom = "PROMO"
        c.restaurar(snap)
        self.assertEqual(c.itens, {"pao": 2})
        self.assertIsNone(c.cupom)

    def test_snapshot_imutavel(self):
        c = Carrinho()
        c.adicionar("a")
        snap = c.salvar()
        c.adicionar("a")
        self.assertEqual(snap.itens, (("a", 1),))
        with self.assertRaises(Exception):
            snap.cupom = "x"

    def test_zelador_varios_niveis(self):
        c = Carrinho()
        z = Zelador(c)
        z.checkpoint()
        c.adicionar("x")
        z.checkpoint()
        c.adicionar("y")
        self.assertTrue(z.voltar())
        self.assertEqual(c.itens, {"x": 1})
        self.assertTrue(z.voltar())
        self.assertEqual(c.itens, {})
        self.assertFalse(z.voltar())


if __name__ == "__main__":
    unittest.main()
