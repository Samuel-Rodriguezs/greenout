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

    def test_top2_imoveis_por_bairro(self):
        self.assertEqual(consulta(self.con, "05_top2_imoveis_por_bairro.sql"), [('Centro', 5, 'casa', 3200.0, 1),
            ('Centro', 2, 'apartamento', 2500.0, 2),
            ('Jardins', 3, 'casa', 4500.0, 1),
            ('Jardins', 4, 'apartamento', 2800.0, 2),
            ('Vila Nova', 8, 'casa', 2600.0, 1)])

    def test_recebimento_mensal_variacao(self):
        self.assertEqual(consulta(self.con, "06_recebimento_mensal_variacao.sql"), [('2025-01', 14800.0, None, None),
            ('2025-02', 11800.0, 14800.0, -3000.0),
            ('2025-03', 4300.0, 11800.0, -7500.0),
            ('2025-04', 13100.0, 4300.0, 8800.0),
            ('2025-05', 13100.0, 13100.0, 0.0),
            ('2025-06', 8500.0, 13100.0, -4600.0)])

    def test_pivot_tipo_situacao(self):
        self.assertEqual(consulta(self.con, "07_pivot_tipo_situacao.sql"), [('apartamento', 11, 4, 3), ('casa', 5, 1, 0), ('sala', 4, 0, 0)])

    def test_vistorias_queda_de_nota(self):
        self.assertEqual(consulta(self.con, "08_vistorias_queda_de_nota.sql"), [(5, '2025-02-28', 'saida', 4, 7, 2),
            (1, '2025-05-20', 'periodica', 6, 8, 3),
            (2, '2025-04-02', 'periodica', 9, 10, 2),
            (8, '2024-12-31', 'saida', 7, 8, 2)])


if __name__ == "__main__":
    unittest.main()
