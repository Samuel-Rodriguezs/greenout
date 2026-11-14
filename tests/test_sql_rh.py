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

    def test_reajustes_historico(self):
        self.assertEqual(consulta(self.con, "04_reajustes_historico.sql"), [('Diego Alves', '2021-07-01', 11000.0, 9000.0, 22.2),
            ('Carla Mendes', '2022-01-01', 18000.0, 15000.0, 20.0),
            ('Fabio Lima', '2023-01-01', 7000.0, 6000.0, 16.7),
            ('Gina Rocha', '2024-03-01', 5200.0, 4500.0, 15.6),
            ('Elaine Souza', '2022-03-01', 11500.0, 10000.0, 15.0),
            ('Diego Alves', '2023-07-01', 12500.0, 11000.0, 13.6),
            ('Iara Nunes', '2024-06-01', 2800.0, 2500.0, 12.0)])

    def test_horas_extras(self):
        self.assertEqual(consulta(self.con, "05_horas_extras.sql"), [('Gina Rocha', 3.5, 170.63), ('Joao Teles', 3.5, 78.75), ('Iara Nunes', 2.0, 52.5)])

    def test_sem_ferias_com_afastamento(self):
        self.assertEqual(consulta(self.con, "06_sem_ferias_com_afastamento.sql"), [('Hugo Prado', 'sem ferias e sem afastamento'),
            ('Iara Nunes', 'afastado sem ferias'),
            ('Joao Teles', 'afastado sem ferias')])


if __name__ == "__main__":
    unittest.main()
