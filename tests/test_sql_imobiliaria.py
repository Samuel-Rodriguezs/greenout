import sqlite3
import unittest
from pathlib import Path

SQL = Path(__file__).resolve().parent.parent / "sql" / "imobiliaria"


def consulta(con, arquivo):
    return con.execute((SQL / arquivo).read_text()).fetchall()


class TestSQLImobiliaria(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.executescript((SQL / "00_schema.sql").read_text())

    def test_schema_carregado(self):
        n = self.con.execute("SELECT COUNT(*) FROM proprietarios").fetchone()[0]
        self.assertEqual(n, 4)

    def test_receita_por_proprietario(self):
        self.assertEqual(consulta(self.con, "01_receita_por_proprietario.sql"), [('Lucia Prado', 2, 29200.0),
            ('Marcos Vieira', 2, 24000.0),
            ('Antonio Gomes', 2, 12400.0)])

    def test_imoveis_vagos(self):
        self.assertEqual(consulta(self.con, "02_imoveis_vagos.sql"), [(5, 'casa', 'Centro', 3200.0),
            (7, 'apartamento', 'Jardins', 2000.0),
            (8, 'casa', 'Vila Nova', 2600.0)])

    def test_atrasos_pagamento(self):
        self.assertEqual(consulta(self.con, "03_atrasos_pagamento.sql"), [('Daniel Esteves', '2025-03', 107, 'em aberto'),
            ('Ana Beatriz', '2025-06', 25, 'em aberto'),
            ('Daniel Esteves', '2025-04', 15, 'pago com atraso'),
            ('Daniel Esteves', '2025-06', 15, 'em aberto'),
            ('Bruno Castro', '2025-04', 10, 'pago com atraso'),
            ('Ana Beatriz', '2025-03', 7, 'pago com atraso'),
            ('Daniel Esteves', '2025-02', 5, 'pago com atraso'),
            ('Camila Dutra', '2025-05', 4, 'pago com atraso')])

    def test_inadimplencia_por_locatario(self):
        self.assertEqual(consulta(self.con, "04_inadimplencia_por_locatario.sql"), [('Daniel Esteves', 6, 4, 66.7),
            ('Camila Dutra', 4, 1, 25.0),
            ('Ana Beatriz', 10, 2, 20.0),
            ('Bruno Castro', 8, 1, 12.5)])


if __name__ == "__main__":
    unittest.main()
