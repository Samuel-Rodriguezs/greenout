import sqlite3
import unittest
from pathlib import Path

SQL = Path(__file__).resolve().parent.parent / "sql"


def banco():
    con = sqlite3.connect(":memory:")
    con.executescript((SQL / "10_vendas_schema.sql").read_text(encoding="utf-8"))
    return con


def consulta(con, arquivo):
    return con.execute((SQL / arquivo).read_text(encoding="utf-8")).fetchall()


class TestSQLVendas(unittest.TestCase):
    def setUp(self):
        self.con = banco()

    def tearDown(self):
        self.con.close()


if __name__ == "__main__":
    unittest.main()
