import sqlite3
import unittest
from pathlib import Path

SQL = Path(__file__).resolve().parent.parent / "sql" / "juridico"


def consulta(con, arquivo):
    return con.execute((SQL / arquivo).read_text()).fetchall()


class TestSQLJuridico(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.executescript((SQL / "00_schema.sql").read_text())

    def test_schema_carregado(self):
        n = self.con.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
        self.assertEqual(n, 6)

    def test_processos_por_advogado(self):
        self.assertEqual(consulta(self.con, "01_processos_por_advogado.sql"), [
            ('Clara Nunes', 2, 150000.0),
            ('Pedro Lacerda', 2, 140000.0)])

    def test_hierarquia_advogados(self):
        self.assertEqual(consulta(self.con, "02_hierarquia_advogados.sql"), [
            ('Helena Barros', 0, 'Helena Barros', 1),
            ('Clara Nunes', 1, 'Helena Barros > Clara Nunes', 2),
            ('Rui Matos', 1, 'Helena Barros > Rui Matos', 3),
            ('Joana Pires', 2, 'Helena Barros > Rui Matos > Joana Pires', 1),
            ('Pedro Lacerda', 2, 'Helena Barros > Rui Matos > Pedro Lacerda', 2)])


if __name__ == "__main__":
    unittest.main()
