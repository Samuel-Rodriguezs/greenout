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

    def test_medicos_mais_ocupados(self):
        self.assertEqual(consulta(self.con, "01_medicos_mais_ocupados.sql"), [
            ("Helena Costa", 3, 900.0), ("Paulo Silva", 3, 750.0),
            ("Marta Rocha", 2, 560.0), ("Ivo Tavares", 2, 300.0)])

    def test_hierarquia_medicos(self):
        self.assertEqual(consulta(self.con, "02_hierarquia_medicos.sql"), [
            ("Helena Costa", 0, "Helena Costa"),
            ("Marta Rocha", 1, "Helena Costa > Marta Rocha"),
            ("Lia Campos", 2, "Helena Costa > Marta Rocha > Lia Campos"),
            ("Paulo Silva", 1, "Helena Costa > Paulo Silva"),
            ("Ivo Tavares", 2, "Helena Costa > Paulo Silva > Ivo Tavares")])

    def test_ranking_por_especialidade(self):
        self.assertEqual(consulta(self.con, "03_ranking_por_especialidade.sql"), [
            ("Cardiologia", "Helena Costa", 900.0, 1), ("Cardiologia", "Paulo Silva", 750.0, 2),
            ("Clínica Geral", "Ivo Tavares", 300.0, 1), ("Clínica Geral", "Lia Campos", 150.0, 2),
            ("Ortopedia", "Marta Rocha", 560.0, 1)])

    def test_intervalo_entre_consultas(self):
        self.assertEqual(consulta(self.con, "04_intervalo_entre_consultas.sql"), [
            ("Ana Lima", "2025-02-15", 36), ("Ana Lima", "2025-03-30", 43),
            ("Bruno Reis", "2025-03-05", 44), ("Elisa Prado", "2025-03-18", 52),
            ("Fábio Nunes", "2025-03-22", 48)])

    def test_internacoes_duracao(self):
        self.assertEqual(consulta(self.con, "05_internacoes_duracao.sql"), [
            ("Elisa Prado", "infarto", "2025-02-20", 10),
            ("Fábio Nunes", "fratura", "em andamento", 9),
            ("Bruno Reis", "arritmia", "2025-01-26", 5),
            ("Carla Dias", "fratura", "2025-02-12", 3),
            ("Bruno Reis", "arritmia", "2025-03-08", 2)])
