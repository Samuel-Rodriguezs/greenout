import sqlite3
import unittest
from pathlib import Path

SQL = Path(__file__).resolve().parent.parent / "sql"


def banco():
    con = sqlite3.connect(":memory:")
    con.executescript((SQL / "10_vendas_schema.sql").read_text(encoding="utf-8"))
    return con


def consulta(con, arquivo):
    return con.execute((SQL / arquivo).read_text(encoding="utf-8")).fetchall()


class TestSQLVendas(unittest.TestCase):
    def setUp(self):
        self.con = banco()

    def tearDown(self):
        self.con.close()

    def test_clientes_grandes_compradores(self):
        self.assertEqual(consulta(self.con, "11_clientes_grandes_compradores.sql"),
                         [("Ana", 3300.0), ("Bruno", 2300.0), ("Eva", 500.0)])

    def test_pedidos_por_cliente(self):
        self.assertEqual(consulta(self.con, "12_pedidos_por_cliente.sql"),
                         [("Ana", 3), ("Bruno", 3), ("Carla", 2), ("Eva", 2),
                          ("Davi", 0), ("Filipe", 0)])

    def test_produtos_acima_da_media(self):
        self.assertEqual(consulta(self.con, "13_produtos_acima_da_media.sql"),
                         [("Notebook", 3000.0), ("Cadeira", 800.0)])

    def test_receita_mensal(self):
        self.assertEqual(consulta(self.con, "14_receita_mensal.sql"),
                         [("2025-01", 3100.0), ("2025-02", 1800.0),
                          ("2025-03", 3910.0), ("2025-04", 1300.0)])

    def test_ranking_clientes(self):
        self.assertEqual(consulta(self.con, "15_ranking_clientes.sql"),
                         [(1, "Ana", 6300.0), (2, "Bruno", 3100.0),
                          (3, "Eva", 500.0), (4, "Carla", 210.0)])

    def test_top2_produtos_por_categoria(self):
        self.assertEqual(consulta(self.con, "16_top2_produtos_por_categoria.sql"),
                         [("Informática", "Notebook", 6000.0),
                          ("Informática", "Teclado", 450.0),
                          ("Móveis", "Cadeira", 2400.0),
                          ("Móveis", "Mesa", 600.0),
                          ("Papelaria", "Agenda", 210.0),
                          ("Papelaria", "Caneta", 150.0)])

    def test_receita_acumulada(self):
        self.assertEqual(consulta(self.con, "17_receita_acumulada.sql"),
                         [("2025-01", 3100.0, 3100.0), ("2025-02", 1800.0, 4900.0),
                          ("2025-03", 3910.0, 8810.0), ("2025-04", 1300.0, 10110.0)])


if __name__ == "__main__":
    unittest.main()
