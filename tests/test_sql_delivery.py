import sqlite3
import unittest
from pathlib import Path

SQL = Path(__file__).resolve().parent.parent / "sql" / "delivery"


def consulta(con, arquivo):
    return con.execute((SQL / arquivo).read_text()).fetchall()


class TestSQLDelivery(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.executescript((SQL / "00_schema.sql").read_text())

    def test_schema_carregado(self):
        n = self.con.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
        self.assertEqual(n, 5)

    def test_faturamento_por_restaurante(self):
        self.assertEqual(consulta(self.con, "01_faturamento_por_restaurante.sql"), [('Trattoria Roma', 4, 9, 429.0),
            ('Burger Lab', 4, 13, 346.0),
            ('Sushi Kyoto', 2, 6, 216.0)])


if __name__ == "__main__":
    unittest.main()
