import sqlite3
import unittest
from pathlib import Path

SQL = Path(__file__).resolve().parent.parent / "sql" / "financas"


def consulta(con, arquivo):
    return con.execute((SQL / arquivo).read_text()).fetchall()


class TestSQLFinancas(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.executescript((SQL / "00_schema.sql").read_text())

    def test_saldo_por_conta(self):
        self.assertEqual(consulta(self.con, "01_saldo_por_conta.sql"),
                         [("Corrente", 4300), ("Poupança", 1000), ("Carteira", 0)])

    def test_saldo_acumulado(self):
        saldos = [r[3] for r in consulta(self.con, "02_saldo_acumulado.sql")]
        self.assertEqual(saldos, [5000, 3500, 2900, 2700, 7700, 6200, 5450, 5150, 4650, 4300])

    def test_gasto_por_mes(self):
        self.assertEqual(consulta(self.con, "03_gasto_por_mes.sql"),
                         [("2024-01", 2300), ("2024-02", 2550), ("2024-03", 850)])

    def test_maior_despesa_por_categoria(self):
        self.assertEqual(consulta(self.con, "04_maior_despesa_por_categoria.sql"), [
            ("Moradia", "Aluguel jan", 1500), ("Alimentação", "Mercado fev", 750),
            ("Lazer", "Show", 350), ("Transporte", "Combustível", 300)])
