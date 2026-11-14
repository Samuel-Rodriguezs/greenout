import sqlite3
import unittest
from pathlib import Path

SQL = Path(__file__).resolve().parent.parent / "sql" / "logistica"


def consulta(con, arquivo):
    return con.execute((SQL / arquivo).read_text()).fetchall()


class TestSQLLogistica(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.executescript((SQL / "00_schema.sql").read_text())

    def test_schema_carregado(self):
        n = self.con.execute("SELECT COUNT(*) FROM depositos").fetchone()[0]
        self.assertEqual(n, 5)

    def test_saldo_por_deposito(self):
        self.assertEqual(consulta(self.con, "01_saldo_por_deposito.sql"), [
            ('CD Campinas', 'Laticínios', 50, 145.0),
            ('CD Campinas', 'Queijos', 40, 1920.0),
            ('CD Campinas', 'Sucos', 260, 1170.0),
            ('CD Curitiba', 'Limpeza', 290, 1244.0),
            ('CD Curitiba', 'Queijos', 50, 1100.0),
            ('CD Porto Alegre', 'Bebidas', 450, 540.0),
            ('CD São Paulo', 'Bebidas', 100, 120.0),
            ('CD São Paulo', 'Queijos', 30, 660.0),
            ('CD São Paulo', 'Sucos', 50, 225.0)])

    def test_lotes_a_vencer(self):
        self.assertEqual(consulta(self.con, "02_lotes_a_vencer.sql"), [
            ('L004', 'Queijo Minas', 'CD São Paulo', 30, '2025-06-10', -5, 'vencido'),
            ('L005', 'Iogurte Natural', 'CD Campinas', 50, '2025-06-25', 10, 'crítico'),
            ('L001', 'Suco de Uva', 'CD São Paulo', 50, '2025-07-01', 16, 'atenção')])

    def test_hierarquia_categorias(self):
        self.assertEqual(consulta(self.con, "03_hierarquia_categorias.sql"), [
            ('Alimentos', 0, 0),
            ('Alimentos > Bebidas', 1, 1),
            ('Alimentos > Bebidas > Sucos', 2, 2),
            ('Alimentos > Laticínios', 1, 1),
            ('Alimentos > Laticínios > Queijos', 2, 2),
            ('Limpeza', 0, 2)])

    def test_rotas_a_partir_de_sao_paulo(self):
        self.assertEqual(consulta(self.con, "04_rotas_a_partir_de_sao_paulo.sql"), [
            ('CD Campinas', 1, 100, '1>2'),
            ('CD Curitiba', 1, 400, '1>3'),
            ('CD Florianópolis', 2, 700, '1>3>5'),
            ('CD Porto Alegre', 2, 1110, '1>3>4')])

    def test_top2_produtos_por_deposito(self):
        self.assertEqual(consulta(self.con, "05_top2_produtos_por_deposito.sql"), [
            ('CD Campinas', 'Iogurte Natural', 100, 1),
            ('CD Campinas', 'Suco de Uva', 40, 2),
            ('CD Curitiba', 'Detergente', 400, 1),
            ('CD Curitiba', 'Desinfetante', 60, 2),
            ('CD Porto Alegre', 'Água Mineral', 150, 1),
            ('CD São Paulo', 'Água Mineral', 900, 1),
            ('CD São Paulo', 'Suco de Uva', 150, 2)])

    def test_saldo_acumulado_lote(self):
        self.assertEqual(consulta(self.con, "06_saldo_acumulado_lote.sql"), [
            ('L001', '2025-04-01', 'E', 200, 200),
            ('L001', '2025-04-20', 'S', 50, 150),
            ('L001', '2025-05-10', 'S', 70, 80),
            ('L001', '2025-06-01', 'S', 30, 50),
            ('L003', '2025-04-10', 'E', 100, 100),
            ('L003', '2025-05-05', 'S', 60, 40),
            ('L003', '2025-05-30', 'S', 40, 0),
            ('L004', '2025-03-15', 'E', 80, 80),
            ('L004', '2025-04-02', 'S', 30, 50),
            ('L004', '2025-05-01', 'S', 20, 30),
            ('L008', '2025-01-15', 'E', 1000, 1000),
            ('L008', '2025-02-15', 'S', 400, 600),
            ('L008', '2025-03-15', 'S', 300, 300),
            ('L008', '2025-04-15', 'S', 200, 100)])

    def test_pontualidade_fornecedores(self):
        self.assertEqual(consulta(self.con, "07_pontualidade_fornecedores.sql"), [
            ('Brasil Clean', 2, 2, 100.0, 13.5),
            ('Agro Vale', 2, 1, 50.0, 11.0),
            ('Lácteos Serra', 2, 0, 0.0, 8.0)])

    def test_curva_abc_ntile(self):
        self.assertEqual(consulta(self.con, "08_curva_abc_ntile.sql"), [
            ('Água Mineral', 1050, 'A'),
            ('Detergente', 400, 'A'),
            ('Suco de Uva', 190, 'A'),
            ('Iogurte Natural', 100, 'B'),
            ('Suco de Laranja', 100, 'B'),
            ('Desinfetante', 60, 'B'),
            ('Queijo Minas', 60, 'C'),
            ('Queijo Parmesão', 0, 'C')])

    def test_produtos_sem_saida(self):
        self.assertEqual(consulta(self.con, "09_produtos_sem_saida.sql"), [
            ('Queijo Parmesão', 40, 1920.0)])

    def test_pivot_saidas_mensais(self):
        self.assertEqual(consulta(self.con, "10_pivot_saidas_mensais.sql"), [
            ('CD São Paulo', 300, 280, 190, 30, 800),
            ('CD Curitiba', 120, 240, 100, 10, 470),
            ('CD Porto Alegre', 0, 150, 0, 0, 150),
            ('CD Campinas', 0, 0, 40, 100, 140)])


if __name__ == "__main__":
    unittest.main()
