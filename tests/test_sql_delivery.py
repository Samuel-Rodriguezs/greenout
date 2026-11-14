import sqlite3
import unittest
from pathlib import Path

SQL = Path(__file__).resolve().parent.parent / "sql" / "delivery"


def consulta(con, arquivo):
    return con.execute((SQL / arquivo).read_text()).fetchall()


class TestSQLDelivery(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.executescript((SQL / "00_schema.sql").read_text())

    def test_schema_carregado(self):
        n = self.con.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
        self.assertEqual(n, 5)

    def test_faturamento_por_restaurante(self):
        self.assertEqual(consulta(self.con, "01_faturamento_por_restaurante.sql"), [('Trattoria Roma', 4, 9, 429.0),
            ('Burger Lab', 4, 13, 346.0),
            ('Sushi Kyoto', 2, 6, 216.0)])

    def test_prato_mais_vendido_por_restaurante(self):
        self.assertEqual(consulta(self.con, "02_prato_mais_vendido_por_restaurante.sql"), [('Burger Lab', 'Cheeseburger', 8),
            ('Sushi Kyoto', 'Temaki', 3),
            ('Trattoria Roma', 'Lasanha', 4)])

    def test_ticket_medio_cliente(self):
        self.assertEqual(consulta(self.con, "03_ticket_medio_cliente.sql"), [('Alice', 4, 117.5, 'alto'),
            ('Clara', 1, 109.0, 'alto'),
            ('Bernardo', 3, 99.33, 'medio'),
            ('Davi', 2, 87.0, 'medio')])

    def test_clientes_sem_pedidos(self):
        self.assertEqual(consulta(self.con, "04_clientes_sem_pedidos.sql"), [('Elisa',)])

    def test_restaurantes_acima_da_media(self):
        self.assertEqual(consulta(self.con, "05_restaurantes_acima_da_media.sql"), [('Burger Lab', 4, 4.25), ('Trattoria Roma', 4, 4.25)])

    def test_desempenho_entregadores(self):
        self.assertEqual(consulta(self.con, "06_desempenho_entregadores.sql"), [('Tiago', 3, 28.3, 1), ('Rafael', 4, 40.0, 2), ('Simone', 3, 40.0, 2)])

    def test_pedidos_por_turno(self):
        self.assertEqual(consulta(self.con, "07_pedidos_por_turno.sql"), [('Burger Lab', 2, 2), ('Sushi Kyoto', 0, 3), ('Trattoria Roma', 3, 1)])

    def test_intervalo_entre_pedidos(self):
        self.assertEqual(consulta(self.con, "08_intervalo_entre_pedidos.sql"), [('Alice', '2025-05-09', 7),
            ('Alice', '2025-06-01', 23),
            ('Alice', '2025-06-14', 13),
            ('Bernardo', '2025-05-17', 7),
            ('Bernardo', '2025-06-08', 22),
            ('Clara', '2025-05-24', 6),
            ('Davi', '2025-06-07', 13)])

    def test_receita_acumulada_diaria(self):
        self.assertEqual(consulta(self.con, "09_receita_acumulada_diaria.sql"), [('2025-05-02', 132.0, 132.0, 13.3),
            ('2025-05-09', 116.0, 248.0, 11.7),
            ('2025-05-10', 97.0, 345.0, 9.8),
            ('2025-05-17', 82.0, 427.0, 8.3),
            ('2025-05-24', 103.0, 530.0, 10.4),
            ('2025-05-25', 68.0, 598.0, 6.9),
            ('2025-06-01', 97.0, 695.0, 9.8),
            ('2025-06-07', 96.0, 791.0, 9.7),
            ('2025-06-08', 100.0, 891.0, 10.1),
            ('2025-06-14', 100.0, 991.0, 10.1)])

    def test_clientes_italiana_e_japonesa(self):
        self.assertEqual(consulta(self.con, "10_clientes_italiana_e_japonesa.sql"), [('Alice',), ('Bernardo',)])


if __name__ == "__main__":
    unittest.main()
