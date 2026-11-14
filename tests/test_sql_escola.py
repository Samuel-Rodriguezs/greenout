import sqlite3
import unittest
from pathlib import Path

SQL = Path(__file__).resolve().parent.parent / "sql" / "escola"


def consulta(con, arquivo):
    return con.execute((SQL / arquivo).read_text()).fetchall()


class TestSQLEscola(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.executescript((SQL / "00_schema.sql").read_text())

    def test_media_por_aluno(self):
        self.assertEqual(consulta(self.con, "01_media_por_aluno.sql"), [
            ("Ana", 8.5), ("Elisa", 8.5), ("Carla", 7.0), ("Fábio", 7.0),
            ("Bruno", 5.5), ("Diego", 4.5)])
