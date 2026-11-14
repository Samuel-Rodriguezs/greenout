import sqlite3
import unittest
from pathlib import Path

SQL = Path(__file__).resolve().parent.parent / "sql" / "imobiliaria"


def consulta(con, arquivo):
    return con.execute((SQL / arquivo).read_text()).fetchall()


class TestSQLImobiliaria(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.executescript((SQL / "00_schema.sql").read_text())

    def test_schema_carregado(self):
        n = self.con.execute("SELECT COUNT(*) FROM proprietarios").fetchone()[0]
        self.assertEqual(n, 4)

    def test_receita_por_proprietario(self):
        self.assertEqual(consulta(self.con, "01_receita_por_proprietario.sql"), [('Lucia Prado', 2, 29200.0),
            ('Marcos Vieira', 2, 24000.0),
            ('Antonio Gomes', 2, 12400.0)])


if __name__ == "__main__":
    unittest.main()
