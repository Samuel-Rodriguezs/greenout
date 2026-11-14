import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from proj_inventario import Inventario, Produto


class TestInventario(unittest.TestCase):
    def setUp(self):
        self.inv = Inventario()
        self.inv.cadastrar(Produto("A1", "caneta", 2.5, 10, minimo=5))
        self.inv.cadastrar(Produto("B2", "caderno", 20.0, 3, minimo=5))

    def test_valor_total(self):
        self.assertAlmostEqual(self.inv.valor_total(), 25.0 + 60.0)

    def test_entrada_saida(self):
        self.inv.saida("A1", 6)
        self.inv.entrada("B2", 4)
        self.assertEqual([p.sku for p in self.inv.abaixo_do_minimo()], ["A1"])

    def test_abaixo_do_minimo(self):
        self.assertEqual([p.sku for p in self.inv.abaixo_do_minimo()], ["B2"])

    def test_estoque_insuficiente(self):
        with self.assertRaises(ValueError):
            self.inv.saida("B2", 4)

    def test_sku_duplicado_e_desconhecido(self):
        with self.assertRaises(ValueError):
            self.inv.cadastrar(Produto("A1", "x", 1))
        with self.assertRaises(KeyError):
            self.inv.entrada("ZZ", 1)

    def test_quantidades_invalidas(self):
        with self.assertRaises(ValueError):
            self.inv.entrada("A1", 0)
        with self.assertRaises(ValueError):
            self.inv.saida("A1", -1)
        with self.assertRaises(ValueError):
            Produto("C", "c", -1)


if __name__ == "__main__":
    unittest.main()
