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

    def test_receita_acumulada_diaria(self):
        self.assertEqual(consulta(self.con, "04_receita_acumulada_diaria.sql"), [
            ("2025-05-01", 1700.0, 1700.0), ("2025-05-02", 1560.0, 3260.0), ("2025-05-03", 1700.0, 4960.0),
            ("2025-05-10", 300.0, 5260.0), ("2025-06-02", 1070.0, 6330.0), ("2025-06-05", 300.0, 6630.0)])

    def test_fidelidade(self):
        self.assertEqual(consulta(self.con, "05_fidelidade.sql"), [
            ("gold", 2, 3350.0), ("sem programa", 3, 1790.0), ("silver", 1, 1490.0)])

    def test_proximo_voo_aeronave(self):
        self.assertEqual(consulta(self.con, "06_proximo_voo_aeronave.sql"), [
            ("A320", "AZ100", "AZ101", 10.0), ("A320", "AZ101", "AZ400", 759.0),
            ("B737", "AZ200", "AZ201", 24.5), ("E195", "AZ300", "AZ301", 169.8),
            ("E195", "AZ301", "AZ500", 620.5)])
