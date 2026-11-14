import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dt_pis import calcular_digito, formatar_pis, gerar_pis, normalizar_pis, validar_pis


class TestPis(unittest.TestCase):
    def test_validos(self) -> None:
        for pis in ("123.45678.91-9", "12345678919"):
            with self.subTest(pis=pis):
                self.assertTrue(validar_pis(pis))

    def test_calculo_manual(self) -> None:
        # 1*3+2*2+3*9+4*8+5*7+6*6+7*5+8*4+9*3+1*2 = 233; 233 % 11 = 2; 11 - 2 = 9
        self.assertEqual(calcular_digito("1234567891"), 9)

    def test_resto_zero_ou_um_gera_digito_zero(self) -> None:
        # soma = 5 para "0000000011" (3*1 + 2*1) => dígito 11 - 5 = 6
        base = "0000000011"
        achado = False
        for n in range(1000):
            b = f"{n:010d}"
            soma = sum(int(c) * p for c, p in zip(b, (3, 2, 9, 8, 7, 6, 5, 4, 3, 2)))
            if soma % 11 in (0, 1):
                self.assertEqual(calcular_digito(b), 0)
                achado = True
        self.assertTrue(achado)
        self.assertEqual(calcular_digito(base), 6)

    def test_invalidos(self) -> None:
        for pis in ("123.45678.91-8", "12345678910", "11111111111", "00000000000", "1234567891", "", "abcdefghijk"):
            with self.subTest(pis=pis):
                self.assertFalse(validar_pis(pis))

    def test_formatar_e_gerar(self) -> None:
        self.assertEqual(formatar_pis("12345678919"), "123.45678.91-9")
        self.assertEqual(gerar_pis("1234567891"), "12345678919")
        self.assertEqual(normalizar_pis("123.45678.91-9"), "12345678919")
        with self.assertRaises(ValueError):
            formatar_pis("123")
        with self.assertRaises(ValueError):
            calcular_digito("123")


if __name__ == "__main__":
    unittest.main()
