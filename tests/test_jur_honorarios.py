import sys
import unittest
from datetime import date
from decimal import Decimal as D
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from jur_honorarios import criar_contrato


class TestHonorarios(unittest.TestCase):
    def test_parcelas_soma_exata(self):
        c = criar_contrato(1, D("1000.00"), 3, date(2024, 1, 31))
        self.assertEqual([p.valor for p in c.parcelas], [D("333.33"), D("333.33"), D("333.34")])
        self.assertEqual(sum(p.valor for p in c.parcelas), D("1000.00"))

    def test_vencimentos_fim_de_mes(self):
        c = criar_contrato(1, D("300"), 3, date(2024, 1, 31))
        self.assertEqual([p.vencimento for p in c.parcelas], [date(2024, 1, 31), date(2024, 2, 29), date(2024, 3, 31)])

    def test_virada_de_ano(self):
        c = criar_contrato(1, D("200"), 2, date(2024, 12, 15))
        self.assertEqual(c.parcelas[1].vencimento, date(2025, 1, 15))

    def test_exito(self):
        c = criar_contrato(1, D("500"), 1, date(2024, 1, 1), D("20"))
        self.assertEqual(c.valor_exito(D("10000.50")), D("2000.10"))
        c.registrar_exito(D("10000"))
        self.assertEqual(c.total_devido, D("2500.00"))
        with self.assertRaises(ValueError):
            c.valor_exito(D("-1"))

    def test_pagamento_e_saldo(self):
        c = criar_contrato(1, D("200"), 2, date(2024, 1, 10))
        self.assertEqual(c.pagar(1, D("150")), D("50"))
        self.assertEqual(c.parcelas[0].saldo, D("0"))
        self.assertEqual(c.saldo(), D("100"))
        with self.assertRaises(KeyError):
            c.pagar(9, D("1"))
        with self.assertRaises(ValueError):
            c.pagar(2, D("0"))

    def test_atraso(self):
        c = criar_contrato(1, D("200"), 2, date(2024, 1, 10))
        c.pagar(1, D("100"))
        self.assertEqual([p.numero for p in c.em_atraso(date(2024, 3, 1))], [2])
        self.assertEqual(c.em_atraso(date(2024, 2, 10)), [])

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            criar_contrato(1, D("100"), 0, date(2024, 1, 1))
        with self.assertRaises(ValueError):
            criar_contrato(1, D("100"), 1, date(2024, 1, 1), D("101"))


if __name__ == "__main__":
    unittest.main()
