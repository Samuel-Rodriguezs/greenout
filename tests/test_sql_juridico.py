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

    def test_prazos_vencendo(self):
        self.assertEqual(consulta(self.con, "03_prazos_vencendo.sql"), [
            ('0002-2024', 'Recurso ordinário', '2025-06-12', -3, 'vencido'),
            ('0007-2024', 'Contrarrazões', '2025-06-15', 0, 'urgente'),
            ('0004-2025', 'Réplica', '2025-06-16', 1, 'urgente'),
            ('0001-2024', 'Apelação', '2025-06-20', 5, 'próximo'),
            ('0003-2023', 'Laudo pericial', '2025-06-30', 15, 'próximo')])

    def test_ranking_causas_por_area(self):
        self.assertEqual(consulta(self.con, "04_ranking_causas_por_area.sql"), [
            ('Civil', '0001-2024', 'Construtora Alfa', 500000.0, 1),
            ('Civil', '0006-2025', 'Mercado Beta', 60000.0, 2),
            ('Civil', '0008-2025', 'Maria Souza', 30000.0, 3),
            ('Família', '0003-2023', 'Maria Souza', 120000.0, 1),
            ('Trabalhista', '0002-2024', 'Construtora Alfa', 80000.0, 1),
            ('Trabalhista', '0004-2025', 'João Pereira', 45000.0, 2),
            ('Tributário', '0007-2024', 'Clínica Gama', 1500000.0, 1),
            ('Tributário', '0005-2022', 'Mercado Beta', 900000.0, 2),
            ('Tributário', '0009-2023', 'Construtora Alfa', 250000.0, 3)])

    def test_intervalo_andamentos(self):
        self.assertEqual(consulta(self.con, "05_intervalo_andamentos.sql"), [
            ('0001-2024', 'contestação', '2024-03-05', 24),
            ('0001-2024', 'perícia', '2024-06-20', 107),
            ('0001-2024', 'sentença', '2025-02-11', 236),
            ('0002-2024', 'audiência', '2024-07-15', 73),
            ('0002-2024', 'sentença', '2025-01-10', 179),
            ('0003-2023', 'despacho', '2024-01-30', 71),
            ('0003-2023', 'perícia', '2025-05-02', 458),
            ('0007-2024', 'liminar', '2024-10-01', 19),
            ('0007-2024', 'recurso', '2025-04-15', 196)])

    def test_parcelas_atrasadas(self):
        self.assertEqual(consulta(self.con, "06_parcelas_atrasadas.sql"), [
            ('Construtora Alfa', 2, '2025-04-05', 71, 273.0, 'crítico'),
            ('Construtora Alfa', 3, '2025-05-05', 41, 183.0, 'alto'),
            ('Clínica Gama', 4, '2025-06-01', 14, 510.0, 'leve'),
            ('Construtora Alfa', 3, '2025-06-10', 5, 250.0, 'leve')])

    def test_clientes_sem_audiencia_futura(self):
        self.assertEqual(consulta(self.con, "07_clientes_sem_audiencia_futura.sql"), [
            ('João Pereira', 1),
            ('Mercado Beta', 1)])

    def test_pivot_area_status(self):
        self.assertEqual(consulta(self.con, "08_pivot_area_status.sql"), [
            ('Civil', 3, 0, 0, 590000.0),
            ('Família', 1, 0, 0, 120000.0),
            ('Trabalhista', 2, 0, 0, 125000.0),
            ('Tributário', 1, 1, 1, 1500000.0)])

    def test_recebimento_acumulado(self):
        self.assertEqual(consulta(self.con, "09_recebimento_acumulado.sql"), [
            ('2025-01', 5000.0, 5000.0, 5.2),
            ('2025-02', 8000.0, 13000.0, 8.3),
            ('2025-03', 26000.0, 39000.0, 26.9),
            ('2025-04', 28000.0, 67000.0, 29.0),
            ('2025-05', 26500.0, 93500.0, 27.5),
            ('2025-06', 3000.0, 96500.0, 3.1)])


if __name__ == "__main__":
    unittest.main()
