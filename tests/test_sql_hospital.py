import sqlite3
import unittest
from pathlib import Path

SQL = Path(__file__).resolve().parent.parent / "sql" / "hospital"


def consulta(con, arquivo):
    return con.execute((SQL / arquivo).read_text()).fetchall()


class TestSQLHospital(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.executescript((SQL / "00_schema.sql").read_text())

    def test_schema_carregado(self):
        n = self.con.execute("SELECT COUNT(*) FROM pacientes").fetchone()[0]
        self.assertEqual(n, 6)
