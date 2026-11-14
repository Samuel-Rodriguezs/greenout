import sys
import unittest
from decimal import Decimal as D
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from jur_captacao import CasoCaptado, ContratoCaptacao, comissao_do_caso, comissoes_do_mes, percentual_efetivo

C = ContratoCaptacao("Rui", D("10"), D("50"), D("400"), ((3, D("2")), (5, D("5"))))


class TestCaptacao(unittest.TestCase):
    def test_percentual_efetivo(self):
        self.assertEqual(percentual_efetivo(C, 1), D("10"))
        self.assertEqual(percentual_efetivo(C, 3), D("12"))
        self.assertEqual(percentual_efetivo(C, 4), D("12"))
        self.assertEqual(percentual_efetivo(C, 9), D("15"))

    def test_comissao(self):
        self.assertEqual(comissao_do_caso(C, D("1000")), D("150.00"))
        self.assertEqual(comissao_do_caso(C, D("1000"), 3), D("170.00"))

    def test_teto(self):
        self.assertEqual(comissao_do_caso(C, D("100000")), D("400.00"))

    def test_zero(self):
        self.assertEqual(comissao_do_caso(C, D("0")), D("50.00"))

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            comissao_do_caso(C, D("-1"))
        with self.assertRaises(ValueError):
            ContratoCaptacao("X", D("101"))
        with self.assertRaises(ValueError):
            ContratoCaptacao("X", D("10"), D("-1"))

    def test_comissoes_do_mes(self):
        contratos = {"Rui": C, "Eva": ContratoCaptacao("Eva", D("20"))}
        casos = [CasoCaptado("Rui", "2024-05", D("1000")) for _ in range(3)]
        casos += [CasoCaptado("Eva", "2024-05", D("500")), CasoCaptado("Rui", "2024-06", D("1000"))]
        r = comissoes_do_mes(contratos, casos, "2024-05")
        self.assertEqual(r, {"Eva": D("100.00"), "Rui": D("510.00")})
        self.assertEqual(comissoes_do_mes(contratos, casos, "2024-07"), {})

    def test_parceiro_sem_contrato(self):
        with self.assertRaises(KeyError):
            comissoes_do_mes({}, [CasoCaptado("Zed", "2024-05", D("1"))], "2024-05")


if __name__ == "__main__":
    unittest.main()
