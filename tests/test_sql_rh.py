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

    def test_ranking_salarial_departamento(self):
        self.assertEqual(consulta(self.con, "03_ranking_salarial_departamento.sql"), [('Comercial', 'Iara Nunes', 2800.0, 1),
            ('Financeiro', 'Elaine Souza', 11500.0, 1),
            ('Financeiro', 'Hugo Prado', 4200.0, 2),
            ('Tecnologia', 'Carla Mendes', 18000.0, 1),
            ('Tecnologia', 'Diego Alves', 12500.0, 2),
            ('Tecnologia', 'Fabio Lima', 7000.0, 3),
            ('Tecnologia', 'Gina Rocha', 5200.0, 4),
            ('Tecnologia', 'Joao Teles', 2400.0, 5)])


if __name__ == "__main__":
    unittest.main()
