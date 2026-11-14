import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_strategy import (Pedido, frete_economico, frete_expresso,
                         frete_gratis_acima)


class TestStrategy(unittest.TestCase):
    def test_estrategias(self):
        self.assertEqual(Pedido(2, 100, frete_economico).frete(), 9.0)
        self.assertEqual(Pedido(2, 100, frete_expresso).frete(), 25.0)

    def test_troca_em_tempo_de_execucao(self):
        p = Pedido(1, 10, frete_economico)
        antes = p.frete()
        p.estrategia = frete_expresso
        self.assertNotEqual(antes, p.frete())

    def test_composicao(self):
        e = frete_gratis_acima(10, frete_economico)
        self.assertEqual(Pedido(10, 100, e).frete(), 0.0)
        self.assertEqual(Pedido(1, 100, e).frete(), 7.0)


if __name__ == "__main__":
    unittest.main()
