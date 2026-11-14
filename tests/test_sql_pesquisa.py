import sqlite3
import unittest
from pathlib import Path

SQL = Path(__file__).resolve().parent.parent / "sql" / "pesquisa"


def consulta(con, arquivo):
    return con.execute((SQL / arquivo).read_text()).fetchall()


class TestSQLPesquisa(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.executescript((SQL / "00_schema.sql").read_text())

    def test_schema_carregado(self):
        n = self.con.execute("SELECT COUNT(*) FROM pesquisadores").fetchone()[0]
        self.assertEqual(n, 8)

    def test_artigos_por_periodico(self):
        self.assertEqual(consulta(self.con, "01_artigos_por_periodico.sql"), [
            ('Journal of AI', 5, 10, 2.0),
            ('Genome Review', 3, 3, 1.0),
            ('Network Letters', 3, 3, 1.0)])


if __name__ == "__main__":
    unittest.main()
