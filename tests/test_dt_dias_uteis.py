import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import dt_dias_uteis as du


class TestDiasUteis(unittest.TestCase):
    def test_eh_dia_util(self) -> None:
        self.assertTrue(du.eh_dia_util(date(2026, 11, 13)))  # sexta
        self.assertFalse(du.eh_dia_util(date(2026, 11, 14)))  # sábado
        self.assertFalse(du.eh_dia_util(date(2026, 11, 15)))  # domingo
        self.assertFalse(du.eh_dia_util(date(2026, 11, 13), [date(2026, 11, 13)]))

    def test_proximo_e_anterior(self) -> None:
        self.assertEqual(du.proximo_dia_util(date(2026, 11, 13)), date(2026, 11, 16))
        self.assertEqual(du.dia_util_anterior(date(2026, 11, 16)), date(2026, 11, 13))
        fer = [date(2026, 11, 16)]
        self.assertEqual(du.proximo_dia_util(date(2026, 11, 13), fer), date(2026, 11, 17))
        self.assertEqual(du.dia_util_anterior(date(2026, 11, 17), fer), date(2026, 11, 13))

    def test_ajustar(self) -> None:
        sab = date(2026, 11, 14)
        self.assertEqual(du.ajustar_para_dia_util(sab), date(2026, 11, 16))
        self.assertEqual(du.ajustar_para_dia_util(sab, para_tras=True), date(2026, 11, 13))
        self.assertEqual(du.ajustar_para_dia_util(date(2026, 11, 12)), date(2026, 11, 12))

    def test_somar(self) -> None:
        self.assertEqual(du.somar_dias_uteis(date(2026, 11, 13), 5), date(2026, 11, 20))
        self.assertEqual(du.somar_dias_uteis(date(2026, 11, 20), -5), date(2026, 11, 13))
        self.assertEqual(du.somar_dias_uteis(date(2026, 11, 13), 0), date(2026, 11, 13))
        self.assertEqual(
            du.somar_dias_uteis(date(2026, 11, 13), 1, [date(2026, 11, 16)]), date(2026, 11, 17)
        )

    def test_contar(self) -> None:
        # segunda a segunda seguinte (exclusivo): 5 dias úteis
        self.assertEqual(du.contar_dias_uteis(date(2026, 11, 9), date(2026, 11, 16)), 5)
        self.assertEqual(du.contar_dias_uteis(date(2026, 11, 14), date(2026, 11, 15)), 0)
        self.assertEqual(du.contar_dias_uteis(date(2026, 11, 9), date(2026, 11, 9)), 0)
        self.assertEqual(du.contar_dias_uteis(date(2026, 11, 16), date(2026, 11, 9)), -5)

    def test_contar_com_feriados(self) -> None:
        fer = [date(2026, 11, 11), date(2026, 11, 14)]  # quarta e sábado (ignorado)
        self.assertEqual(du.contar_dias_uteis(date(2026, 11, 9), date(2026, 11, 16), fer), 4)
        # feriado fora do intervalo não conta
        self.assertEqual(du.contar_dias_uteis(date(2026, 11, 12), date(2026, 11, 16), fer), 2)

    def test_contar_consistente_com_forca_bruta(self) -> None:
        fer = {date(2026, 4, 3), date(2026, 4, 21), date(2026, 5, 1)}
        ini = date(2026, 3, 18)
        for delta in range(0, 90):
            fim = ini + timedelta(days=delta)
            bruto = sum(1 for i in range(delta) if du.eh_dia_util(ini + timedelta(days=i), fer))
            self.assertEqual(du.contar_dias_uteis(ini, fim, fer), bruto)


if __name__ == "__main__":
    unittest.main()
