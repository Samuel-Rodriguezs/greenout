import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fin_custo_medio import Posicao, preco_medio_ponderado


class TestCustoMedio(unittest.TestCase):
    def test_pm_ponderado(self):
        self.assertAlmostEqual(preco_medio_ponderado([(100, 10), (50, 13)]), 11.0)

    def test_pm_vazio(self):
        with self.assertRaises(ValueError):
            preco_medio_ponderado([])

    def test_compras_e_venda(self):
        p = Posicao()
        p.comprar(100, 10)
        p.comprar(50, 13)
        self.assertAlmostEqual(p.custo_medio, 11.0)
        lucro = p.vender(60, 12)
        self.assertAlmostEqual(lucro, 60.0)
        self.assertAlmostEqual(p.quantidade, 90)
        self.assertAlmostEqual(p.custo_medio, 11.0)
        self.assertAlmostEqual(p.lucro_nao_realizado(10), -90.0)

    def test_taxas(self):
        p = Posicao()
        p.comprar(10, 10, taxa=5)  # custo 105 -> médio 10,5
        self.assertAlmostEqual(p.custo_medio, 10.5)
        self.assertAlmostEqual(p.vender(10, 11, taxa=2), 10 * 0.5 - 2)
        self.assertEqual(p.quantidade, 0)
        self.assertEqual(p.custo_medio, 0.0)

    def test_prejuizo(self):
        p = Posicao()
        p.comprar(10, 10)
        self.assertAlmostEqual(p.vender(4, 8), -8.0)
        self.assertAlmostEqual(p.lucro_realizado, -8.0)

    def test_erros(self):
        p = Posicao()
        p.comprar(1, 1)
        with self.assertRaises(ValueError):
            p.vender(2, 1)
        with self.assertRaises(ValueError):
            p.comprar(0, 1)
        with self.assertRaises(ValueError):
            p.vender(1, -1)


if __name__ == "__main__":
    unittest.main()
