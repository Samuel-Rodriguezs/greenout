import sqlite3
import unittest
from pathlib import Path

SQL = Path(__file__).resolve().parent.parent / "sql" / "logistica"


def consulta(con, arquivo):
    return con.execute((SQL / arquivo).read_text()).fetchall()


class TestSQLLogistica(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.executescript((SQL / "00_schema.sql").read_text())

    def test_schema_carregado(self):
        n = self.con.execute("SELECT COUNT(*) FROM depositos").fetchone()[0]
        self.assertEqual(n, 5)

    def test_saldo_por_deposito(self):
        self.assertEqual(consulta(self.con, "01_saldo_por_deposito.sql"), [
            ('CD Campinas', 'Laticínios', 50, 145.0),
            ('CD Campinas', 'Queijos', 40, 1920.0),
            ('CD Campinas', 'Sucos', 260, 1170.0),
            ('CD Curitiba', 'Limpeza', 290, 1244.0),
            ('CD Curitiba', 'Queijos', 50, 1100.0),
            ('CD Porto Alegre', 'Bebidas', 450, 540.0),
            ('CD São Paulo', 'Bebidas', 100, 120.0),
            ('CD São Paulo', 'Queijos', 30, 660.0),
            ('CD São Paulo', 'Sucos', 50, 225.0)])


if __name__ == "__main__":
    unittest.main()
