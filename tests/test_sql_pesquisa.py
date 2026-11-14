import sqlite3
import unittest
from pathlib import Path

SQL = Path(__file__).resolve().parent.parent / "sql" / "pesquisa"


def consulta(con, arquivo):
    return con.execute((SQL / arquivo).read_text()).fetchall()


class TestSQLPesquisa(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.executescript((SQL / "00_schema.sql").read_text())

    def test_schema_carregado(self):
        n = self.con.execute("SELECT COUNT(*) FROM pesquisadores").fetchone()[0]
        self.assertEqual(n, 8)

    def test_artigos_por_periodico(self):
        self.assertEqual(consulta(self.con, "01_artigos_por_periodico.sql"), [
            ('Journal of AI', 5, 10, 2.0),
            ('Genome Review', 3, 3, 1.0),
            ('Network Letters', 3, 3, 1.0)])

    def test_indice_h(self):
        self.assertEqual(consulta(self.con, "02_indice_h.sql"), [
            ('Ana Prado', 4, 2),
            ('Bruno Castro', 4, 2),
            ('Carla Mendes', 4, 2),
            ('Diego Ramos', 4, 2),
            ('Elena Fischer', 3, 1),
            ('Felipe Tanaka', 1, 1),
            ('Gabi Alves', 3, 1),
            ('Hugo Lima', 2, 1)])

    def test_cadeia_de_citacoes(self):
        self.assertEqual(consulta(self.con, "03_cadeia_de_citacoes.sql"), [
            ('Redes Neurais Esparsas', 2018, 1),
            ('Poda de Modelos', 2021, 1),
            ('Treinamento Federado', 2022, 1),
            ('Compressão de Embeddings', 2023, 1),
            ('Atenção Eficiente', 2019, 2)])

    def test_arvore_de_orientacao(self):
        self.assertEqual(consulta(self.con, "04_arvore_de_orientacao.sql"), [
            ('Ana Prado', 0, 'Ana Prado', 4),
            ('Bruno Castro', 1, 'Ana Prado > Bruno Castro', 1),
            ('Diego Ramos', 2, 'Ana Prado > Bruno Castro > Diego Ramos', 0),
            ('Carla Mendes', 1, 'Ana Prado > Carla Mendes', 1),
            ('Gabi Alves', 2, 'Ana Prado > Carla Mendes > Gabi Alves', 0),
            ('Elena Fischer', 0, 'Elena Fischer', 0),
            ('Felipe Tanaka', 0, 'Felipe Tanaka', 1),
            ('Hugo Lima', 1, 'Felipe Tanaka > Hugo Lima', 0)])

    def test_artigo_mais_citado_por_area(self):
        self.assertEqual(consulta(self.con, "05_artigo_mais_citado_por_area.sql"), [
            ('Aprendizado Profundo', 'Redes Neurais Esparsas', 4),
            ('Inteligência Artificial', 'Poda de Modelos', 3),
            ('Genômica', 'Sequenciamento Rápido', 2),
            ('Redes', 'Roteamento Adaptativo', 2)])

    def test_producao_anual(self):
        self.assertEqual(consulta(self.con, "06_producao_anual.sql"), [
            (2018, 1, None, None, 1),
            (2019, 2, 1, 1, 1),
            (2020, 1, 2, -1, 1),
            (2021, 2, 1, 1, 1),
            (2022, 2, 2, 0, 1),
            (2023, 2, 2, 0, 1),
            (2024, 2, 2, 0, 1)])


if __name__ == "__main__":
    unittest.main()
