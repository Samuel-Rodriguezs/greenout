import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_facade import Estoque, Frete, LojaFacade, Pagamento


class TestFacade(unittest.TestCase):
    def montar(self, saldo=100.0):
        e, p = Estoque({"cam": 5}), Pagamento(saldo)
        return LojaFacade(e, p, Frete()), e, p

    def test_sucesso(self):
        loja, e, p = self.montar()
        self.assertEqual(loja.comprar("cam", 2, 20.0), "pedido confirmado: 54.00")
        self.assertEqual(e.itens["cam"], 3)
        self.assertEqual(p.saldo, 46.0)

    def test_sem_estoque(self):
        loja, e, p = self.montar()
        self.assertEqual(loja.comprar("cam", 9, 1.0), "sem estoque")
        self.assertEqual(p.saldo, 100.0)

    def test_pagamento_recusado_devolve_estoque(self):
        loja, e, p = self.montar(saldo=10)
        self.assertEqual(loja.comprar("cam", 2, 20.0), "pagamento recusado")
        self.assertEqual(e.itens["cam"], 5)


if __name__ == "__main__":
    unittest.main()
