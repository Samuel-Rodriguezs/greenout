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


if __name__ == "__main__":
    unittest.main()
