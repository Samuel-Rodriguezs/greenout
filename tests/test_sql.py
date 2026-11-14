import sqlite3
import unittest
from pathlib import Path

SQL = Path(__file__).resolve().parent.parent / "sql"


def banco():
    con = sqlite3.connect(":memory:")
    con.executescript((SQL / "00_schema.sql").read_text())
    return con


def consulta(con, arquivo):
    return con.execute((SQL / arquivo).read_text()).fetchall()


class TestSQL(unittest.TestCase):
    def setUp(self):
        self.con = banco()

    def test_join(self):
        r = consulta(self.con, "01_join.sql")
        self.assertEqual(len(r), 4)  # Eva não tem departamento
        self.assertIn(("Ana", "TI"), r)

    def test_agregacao(self):
        r = {nome: (total, media) for nome, total, media in consulta(self.con, "02_agregacao.sql")}
        self.assertEqual(r["TI"], (2, 7000.0))
        self.assertEqual(r["Financeiro"], (1, 7000.0))

    def test_sem_departamento(self):
        self.assertEqual(consulta(self.con, "03_sem_departamento.sql"), [("Eva",)])

    def test_acima_da_media(self):
        # média = 6000
        self.assertEqual(consulta(self.con, "04_acima_da_media.sql"),
                         [("Ana", 8000.0), ("Davi", 7000.0)])


if __name__ == "__main__":
    unittest.main()
