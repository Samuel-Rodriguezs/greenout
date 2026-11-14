import sys
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dom_rescisao import (anos_completos, dias_aviso_previo, meses_completos,
                          rescisao_sem_justa_causa)

D = Decimal


class TestDomRescisao(unittest.TestCase):
    def test_aviso_proporcional(self):
        self.assertEqual(dias_aviso_previo(date(2024, 1, 10), date(2024, 6, 1)), 30)
        self.assertEqual(dias_aviso_previo(date(2023, 1, 10), date(2024, 1, 10)), 33)
        self.assertEqual(dias_aviso_previo(date(2023, 1, 10), date(2024, 1, 9)), 30)
        self.assertEqual(dias_aviso_previo(date(2000, 1, 1), date(2024, 1, 1)), 90)
        self.assertEqual(dias_aviso_previo(date(2004, 1, 1), date(2024, 1, 1)), 90)

    def test_meses_completos(self):
        self.assertEqual(meses_completos(date(2024, 1, 31), date(2024, 2, 29)), 1)
        self.assertEqual(meses_completos(date(2024, 1, 10), date(2024, 6, 20)), 5)
        self.assertEqual(anos_completos(date(2022, 1, 10), date(2024, 6, 20)), 2)
        with self.assertRaises(ValueError):
            meses_completos(date(2024, 2, 1), date(2024, 1, 1))

    def test_rescisao_completa(self):
        r = rescisao_sem_justa_causa("3000", date(2022, 1, 10), date(2024, 6, 20), "10000")
        self.assertEqual(r.saldo_salario, D("2000.00"))      # 20 dias
        self.assertEqual(r.aviso_previo, D("3600.00"))       # 36 dias
        self.assertEqual(r.decimo_terceiro, D("1500.00"))    # 6/12
        self.assertEqual(r.ferias_proporcionais, D("1666.67"))  # 5/12: 1250 + 416,67
        self.assertEqual(r.multa_fgts, D("4000.00"))
        self.assertEqual(r.total, D("12766.67"))

    def test_aviso_trabalhado(self):
        r = rescisao_sem_justa_causa("3000", date(2022, 1, 10), date(2024, 6, 20),
                                     aviso_indenizado=False)
        self.assertEqual(r.aviso_previo, D("0.00"))
        self.assertEqual(r.multa_fgts, D("0.00"))

    def test_admitido_no_mesmo_ano(self):
        # admissão 01/03, demissão 31/05: 3 avos de 13º; ferias 3 meses
        r = rescisao_sem_justa_causa("1200", date(2024, 3, 1), date(2024, 5, 31))
        self.assertEqual(r.decimo_terceiro, D("300.00"))
        self.assertEqual(r.ferias_proporcionais, D("400.00"))  # 300 + 100

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            rescisao_sem_justa_causa("1000", date(2024, 5, 1), date(2024, 4, 1))
        with self.assertRaises(ValueError):
            rescisao_sem_justa_causa("-1", date(2024, 1, 1), date(2024, 4, 1))


if __name__ == "__main__":
    unittest.main()
