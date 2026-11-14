import sqlite3
import unittest
from pathlib import Path

SQL = Path(__file__).resolve().parent.parent / "sql" / "streaming"


def consulta(con, arquivo):
    return con.execute((SQL / arquivo).read_text()).fetchall()


class TestSQLStreaming(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.executescript((SQL / "00_schema.sql").read_text())

    def test_schema_carregado(self):
        n = self.con.execute("SELECT COUNT(*) FROM titulos").fetchone()[0]
        self.assertEqual(n, 5)

    def test_minutos_por_usuario(self):
        self.assertEqual(consulta(self.con, "01_minutos_por_usuario.sql"), [("Ana", 283, 3), ("Cris", 267, 3), ("Edu", 260, 2)])

    def test_ranking_notas(self):
        self.assertEqual(consulta(self.con, "02_ranking_notas.sql"), [
            ("Codigo Zero", 4.5, 2, 1), ("O Ultimo Farol", 4.5, 2, 1), ("Noite Eterna", 4.0, 3, 3),
            ("Riso Facil", 3.5, 2, 4), ("Orbita", 3.0, 1, 5)])

    def test_top2_titulos_por_tipo(self):
        self.assertEqual(consulta(self.con, "03_top2_titulos_por_tipo.sql"), [
            ("filme", "O Ultimo Farol", 220), ("filme", "Orbita", 185),
            ("serie", "Noite Eterna", 348), ("serie", "Codigo Zero", 137)])
