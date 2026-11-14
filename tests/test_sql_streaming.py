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

    def test_visualizacoes_por_semana(self):
        self.assertEqual(consulta(self.con, "04_visualizacoes_por_semana.sql"), [
            ("2025-01-06", 5, 173), ("2025-01-13", 1, 30), ("2025-01-20", 2, 92), ("2025-01-27", 2, 65),
            ("2025-02-03", 3, 210), ("2025-02-10", 4, 260), ("2025-02-17", 0, 0), ("2025-02-24", 2, 160),
            ("2025-03-03", 0, 0)])

    def test_retorno_apos_pausa(self):
        self.assertEqual(consulta(self.con, "05_retorno_apos_pausa.sql"), [
            ("Ana", "2025-01-18", 7), ("Ana", "2025-02-02", 15), ("Ana", "2025-02-14", 12),
            ("Beto", "2025-02-01", 20), ("Cris", "2025-02-03", 13), ("Cris", "2025-03-02", 27),
            ("Edu", "2025-03-01", 17)])

    def test_maratonistas(self):
        self.assertEqual(consulta(self.con, "06_maratonistas.sql"), [
            ("Ana", "Noite Eterna"), ("Beto", "Riso Facil"), ("Cris", "Codigo Zero"), ("Edu", "Noite Eterna")])
