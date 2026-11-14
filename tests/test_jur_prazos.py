import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from jur_prazos import (Alerta, Prazo, Suspensao, alertas, calcular_vencimento, classificar,
                        dias_uteis_restantes, prorrogar_se_nao_util, recesso_forense)


class TestPrazos(unittest.TestCase):
    def test_simples(self):
        self.assertEqual(calcular_vencimento(date(2024, 3, 4), 5), date(2024, 3, 11))

    def test_intimacao_sexta(self):
        self.assertEqual(calcular_vencimento(date(2024, 3, 8), 1), date(2024, 3, 11))

    def test_feriado(self):
        self.assertEqual(calcular_vencimento(date(2024, 3, 4), 5, feriados=[date(2024, 3, 6)]), date(2024, 3, 12))

    def test_recesso(self):
        v = calcular_vencimento(date(2024, 12, 18), 5, suspensoes=[recesso_forense(2024)])
        # 19/12 (1); recesso até 20/01; 21, 22, 23, 24/01 (2 a 5)
        self.assertEqual(v, date(2025, 1, 24))

    def test_invalido(self):
        with self.assertRaises(ValueError):
            calcular_vencimento(date(2024, 3, 4), 0)
        with self.assertRaises(ValueError):
            Suspensao(date(2024, 2, 2), date(2024, 2, 1))

    def test_restantes(self):
        self.assertEqual(dias_uteis_restantes(date(2024, 3, 4), date(2024, 3, 11)), 5)
        self.assertEqual(dias_uteis_restantes(date(2024, 3, 11), date(2024, 3, 4)), -5)
        self.assertEqual(dias_uteis_restantes(date(2024, 3, 4), date(2024, 3, 4)), 0)

    def test_classificar(self):
        h = date(2024, 3, 4)
        self.assertEqual(classificar(h, date(2024, 3, 1)), Alerta.VENCIDO)
        self.assertEqual(classificar(h, h), Alerta.HOJE)
        self.assertEqual(classificar(h, date(2024, 3, 6)), Alerta.URGENTE)
        self.assertEqual(classificar(h, date(2024, 3, 8)), Alerta.ATENCAO)
        self.assertEqual(classificar(h, date(2024, 3, 20)), Alerta.NORMAL)

    def test_alertas_ordenados(self):
        h = date(2024, 3, 4)
        ps = [Prazo("a", "x", date(2024, 4, 30)), Prazo("b", "y", date(2024, 3, 6)), Prazo("c", "z", date(2024, 3, 1))]
        r = alertas(ps, h)
        self.assertEqual([p.processo for p, _ in r], ["c", "b"])

    def test_prorrogar(self):
        self.assertEqual(prorrogar_se_nao_util(date(2024, 3, 9)), date(2024, 3, 11))
        self.assertEqual(prorrogar_se_nao_util(date(2024, 3, 8)), date(2024, 3, 8))
        self.assertEqual(prorrogar_se_nao_util(date(2024, 3, 8), [date(2024, 3, 8)]), date(2024, 3, 11))


if __name__ == "__main__":
    unittest.main()
