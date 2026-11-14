import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fin_order_book import LivroOfertas, Negocio


class TestLivroOfertas(unittest.TestCase):
    def setUp(self):
        self.livro = LivroOfertas()

    def test_sem_cruzamento_fica_no_livro(self):
        self.livro.enviar("compra", 10, 99.0)
        self.livro.enviar("venda", 5, 101.0)
        self.assertEqual(self.livro.melhor_compra(), 99.0)
        self.assertEqual(self.livro.melhor_venda(), 101.0)
        self.assertAlmostEqual(self.livro.spread(), 2.0)

    def test_negocia_ao_preco_da_ordem_em_repouso(self):
        id_v, _ = self.livro.enviar("venda", 10, 100.0)
        id_c, neg = self.livro.enviar("compra", 4, 102.0)
        self.assertEqual(neg, [Negocio(100.0, 4, id_c, id_v)])
        self.assertEqual(self.livro.profundidade("venda"), [(100.0, 6)])

    def test_prioridade_preco_e_tempo(self):
        a, _ = self.livro.enviar("venda", 5, 101.0)
        b, _ = self.livro.enviar("venda", 5, 100.0)
        c, _ = self.livro.enviar("venda", 5, 100.0)
        _, neg = self.livro.enviar("compra", 12, 101.0)
        self.assertEqual([(n.id_venda, n.preco, n.quantidade) for n in neg],
                         [(b, 100.0, 5), (c, 100.0, 5), (a, 101.0, 2)])
        self.assertEqual(self.livro.profundidade("venda"), [(101.0, 3)])

    def test_saldo_limite_vira_oferta(self):
        self.livro.enviar("venda", 3, 100.0)
        self.livro.enviar("compra", 10, 100.0)
        self.assertIsNone(self.livro.melhor_venda())
        self.assertEqual(self.livro.profundidade("compra"), [(100.0, 7)])

    def test_ordem_a_mercado_descarta_saldo(self):
        self.livro.enviar("venda", 3, 100.0)
        _, neg = self.livro.enviar("compra", 10)
        self.assertEqual(sum(n.quantidade for n in neg), 3)
        self.assertIsNone(self.livro.melhor_compra())

    def test_venda_casa_com_compras(self):
        self.livro.enviar("compra", 5, 98.0)
        self.livro.enviar("compra", 5, 99.0)
        _, neg = self.livro.enviar("venda", 7, 98.0)
        self.assertEqual([(n.preco, n.quantidade) for n in neg], [(99.0, 5), (98.0, 2)])
        self.assertEqual(self.livro.profundidade("compra"), [(98.0, 3)])

    def test_cancelar(self):
        i, _ = self.livro.enviar("compra", 5, 98.0)
        self.assertTrue(self.livro.cancelar(i))
        self.assertFalse(self.livro.cancelar(i))
        self.assertIsNone(self.livro.melhor_compra())
        self.assertIsNone(self.livro.spread())

    def test_erros(self):
        with self.assertRaises(ValueError):
            self.livro.enviar("x", 1, 1.0)
        with self.assertRaises(ValueError):
            self.livro.enviar("compra", 0, 1.0)
        with self.assertRaises(ValueError):
            self.livro.enviar("compra", 1, -1.0)
        with self.assertRaises(ValueError):
            self.livro.profundidade("y")


if __name__ == "__main__":
    unittest.main()
