import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from jur_produtividade import Atividade, destaque, relatorio, total_horas

ATIV = [
    Atividade("Ana", date(2024, 5, 2), "peca", 3.0, True),
    Atividade("Ana", date(2024, 5, 3), "peca", 2.5, False),
    Atividade("Ana", date(2024, 5, 4), "audiencia", 1.0),
    Atividade("Bia", date(2024, 5, 2), "peca", 8.0, True),
    Atividade("Bia", date(2024, 6, 2), "peca", 9.0, True),  # fora do período
]


class TestProdutividade(unittest.TestCase):
    def test_relatorio(self):
        r = relatorio(ATIV, date(2024, 5, 1), date(2024, 5, 31))
        self.assertEqual([x.advogado for x in r], ["Bia", "Ana"])
        ana = r[1]
        self.assertEqual(ana.atividades, 3)
        self.assertEqual(ana.horas, 6.5)
        self.assertEqual(ana.por_tipo, {"audiencia": 1, "peca": 2})
        self.assertEqual(ana.taxa_prazos, 50.0)
        self.assertEqual(ana.horas_por_atividade, 2.17)
        self.assertEqual(r[0].taxa_prazos, 100.0)

    def test_sem_prazos(self):
        r = relatorio([Atividade("Cai", date(2024, 5, 1), "reuniao", 1)], date(2024, 5, 1), date(2024, 5, 1))
        self.assertIsNone(r[0].taxa_prazos)

    def test_periodo_inclusivo_e_vazio(self):
        self.assertEqual(len(relatorio(ATIV, date(2024, 5, 2), date(2024, 5, 2))), 2)
        self.assertEqual(relatorio(ATIV, date(2020, 1, 1), date(2020, 1, 2)), [])

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            relatorio(ATIV, date(2024, 5, 2), date(2024, 5, 1))
        with self.assertRaises(ValueError):
            relatorio([Atividade("X", date(2024, 5, 1), "peca", -1)], date(2024, 5, 1), date(2024, 5, 1))

    def test_destaque_e_total(self):
        r = relatorio(ATIV, date(2024, 5, 1), date(2024, 5, 31))
        self.assertEqual(destaque(r), "Ana")
        self.assertIsNone(destaque([]))
        self.assertEqual(total_horas(r), 14.5)


if __name__ == "__main__":
    unittest.main()
