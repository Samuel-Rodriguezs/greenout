import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import gen_pedidos as g

INI = datetime(2025, 3, 1, 8, 0, 0)
PRECOS = dict(g.CATALOGO)


class TestGenPedidos(unittest.TestCase):
    def test_determinismo(self):
        self.assertEqual(g.gerar_pedidos(1, 50, INI), g.gerar_pedidos(1, 50, INI))
        self.assertNotEqual(g.gerar_pedidos(1, 50, INI), g.gerar_pedidos(2, 50, INI))

    def test_datas_estritamente_crescentes(self):
        ps = g.gerar_pedidos(3, 200, INI)
        datas = [p.criado_em for p in ps]
        self.assertTrue(all(a < b for a, b in zip(datas, datas[1:])))
        self.assertGreater(datas[0], INI)

    def test_numeracao_sequencial(self):
        self.assertEqual([p.numero for p in g.gerar_pedidos(3, 30, INI)], list(range(1, 31)))

    def test_totais_coerentes(self):
        for p in g.gerar_pedidos(4, 300, INI):
            self.assertGreaterEqual(len(p.itens), 1)
            nomes = [i.produto for i in p.itens]
            self.assertEqual(len(nomes), len(set(nomes)))
            for i in p.itens:
                self.assertEqual(i.preco_unitario, PRECOS[i.produto])
                self.assertTrue(1 <= i.quantidade <= 5)
            bruto = sum(i.preco_unitario * i.quantidade for i in p.itens)
            self.assertEqual(p.total, bruto - p.desconto + p.frete)
            self.assertTrue(0 <= p.desconto <= bruto)
            self.assertGreater(p.total, 0)
            self.assertIn(p.status, g.STATUS)

    def test_frete_gratis_acima_de_200(self):
        for p in g.gerar_pedidos(5, 400, INI):
            liquido = p.total - p.frete
            self.assertEqual(p.frete == 0, liquido >= 20000)

    def test_clientes_no_intervalo(self):
        ps = g.gerar_pedidos(6, 200, INI, n_clientes=5)
        self.assertTrue(all(1 <= p.cliente_id <= 5 for p in ps))
        with self.assertRaises(ValueError):
            g.gerar_pedidos(6, 1, INI, n_clientes=0)


if __name__ == "__main__":
    unittest.main()
