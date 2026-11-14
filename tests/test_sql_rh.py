import sqlite3
import unittest
from pathlib import Path

SQL = Path(__file__).resolve().parent.parent / "sql" / "rh"


def consulta(con, arquivo):
    return con.execute((SQL / arquivo).read_text()).fetchall()


class TestSQLRh(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.executescript((SQL / "00_schema.sql").read_text())

    def test_schema_carregado(self):
        n = self.con.execute("SELECT COUNT(*) FROM funcionarios").fetchone()[0]
        self.assertEqual(n, 8)

    def test_folha_por_departamento(self):
        self.assertEqual(consulta(self.con, "01_folha_por_departamento.sql"), [('Tecnologia', 5, 45100.0, 9020.0), ('Financeiro', 2, 15700.0, 7850.0)])

    def test_hierarquia_cargos(self):
        self.assertEqual(consulta(self.con, "02_hierarquia_cargos.sql"), [('Diretor', 0, 'Diretor', 1),
            ('Gerente', 1, 'Diretor > Gerente', 2),
            ('Coordenador', 2, 'Diretor > Gerente > Coordenador', 1),
            ('Analista', 3, 'Diretor > Gerente > Coordenador > Analista', 2),
            ('Assistente', 4, 'Diretor > Gerente > Coordenador > Analista > Assistente', 2)])


if __name__ == "__main__":
    unittest.main()
