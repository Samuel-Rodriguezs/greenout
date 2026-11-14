import sqlite3
import unittest
from pathlib import Path

SQL = Path(__file__).resolve().parent.parent / "sql" / "biblioteca"


def consulta(con, arquivo):
    return con.execute((SQL / arquivo).read_text()).fetchall()


class TestSQLBiblioteca(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.executescript((SQL / "00_schema.sql").read_text())

    def test_atrasados(self):
        self.assertEqual(consulta(self.con, "01_atrasados.sql"),
                         [("Ana", "A Hora da Estrela", 36), ("Carla", "Dom Casmurro", 12)])
