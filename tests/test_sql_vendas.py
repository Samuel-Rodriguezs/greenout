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


if __name__ == "__main__":
    unittest.main()
