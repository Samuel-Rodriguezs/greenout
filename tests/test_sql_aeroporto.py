import sqlite3
import unittest
from pathlib import Path

SQL = Path(__file__).resolve().parent.parent / "sql" / "aeroporto"


def consulta(con, arquivo):
    return con.execute((SQL / arquivo).read_text()).fetchall()


class TestSQLAeroporto(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.executescript((SQL / "00_schema.sql").read_text())

    def test_schema_carregado(self):
        n = self.con.execute("SELECT COUNT(*) FROM voos").fetchone()[0]
        self.assertEqual(n, 8)

    def test_ocupacao_por_voo(self):
        self.assertEqual(consulta(self.con, "01_ocupacao_por_voo.sql"), [
            ("AZ200", "B737", 3, 1.88), ("AZ300", "E195", 2, 1.69), ("AZ100", "A320", 3, 1.67),
            ("AZ201", "B737", 2, 1.25), ("AZ400", "A320", 2, 1.11), ("AZ301", "E195", 1, 0.85),
            ("AZ500", "E195", 1, 0.85), ("AZ101", "A320", 1, 0.56)])

    def test_receita_por_rota(self):
        self.assertEqual(consulta(self.con, "02_receita_por_rota.sql"), [
            ("GRU-CWB", 5, 2450.0), ("GRU-REC", 3, 1560.0), ("REC-GRU", 2, 1230.0)])

    def test_destinos_com_conexao(self):
        self.assertEqual(consulta(self.con, "03_destinos_com_conexao.sql"), [("GRU", 1), ("POA", 1), ("REC", 2)])
