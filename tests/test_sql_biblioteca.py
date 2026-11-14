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

    def test_mais_emprestados(self):
        self.assertEqual(consulta(self.con, "02_mais_emprestados.sql"),
                         [("Dom Casmurro", 3), ("Capitães da Areia", 2), ("A Hora da Estrela", 1)])

    def test_disponibilidade(self):
        self.assertEqual(consulta(self.con, "03_disponibilidade.sql"), [
            ("A Hora da Estrela", 0), ("Capitães da Areia", 1), ("Dom Casmurro", 1),
            ("Gabriela", 0), ("Memórias Póstumas", 0), ("Perto do Coração Selvagem", 1)])

    def test_ranking_leitores(self):
        self.assertEqual(consulta(self.con, "04_ranking_leitores.sql"),
                         [("Ana", 4, 1), ("Bruno", 2, 2), ("Carla", 2, 2), ("Diego", 0, 4)])

    def test_nunca_emprestados(self):
        self.assertEqual(consulta(self.con, "05_nunca_emprestados.sql"),
                         [("Perto do Coração Selvagem",)])

    def test_emprestimos_por_autor(self):
        self.assertEqual(consulta(self.con, "06_emprestimos_por_autor.sql"),
                         [("Machado de Assis", 4), ("Jorge Amado", 3), ("Clarice Lispector", 1)])
