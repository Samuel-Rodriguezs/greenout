import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dt_cnh import calcular_digitos, gerar_cnh, normalizar_cnh, validar_cnh


class TestCnh(unittest.TestCase):
    def test_validos_conhecidos(self) -> None:
        for cnh in ("02650306461", "0265030646 1", "026.503.064-61"):
            with self.subTest(cnh=cnh):
                self.assertTrue(validar_cnh(cnh))

    def test_calculo_manual(self) -> None:
        # base 026503064: soma com pesos 9..1 dá resto 6; com pesos 1..9 dá resto 1
        base = "026503064"
        soma1 = sum(int(c) * p for c, p in zip(base, range(9, 0, -1)))
        soma2 = sum(int(c) * p for c, p in zip(base, range(1, 10)))
        self.assertEqual(soma1 % 11, 6)
        self.assertEqual(soma2 % 11, 1)
        self.assertEqual(calcular_digitos(base), "61")

    def test_primeiro_digito_acima_de_nove_gera_desconto(self) -> None:
        # procura bases em que soma1 % 11 >= 10 e confere a regra do desconto
        achados = 0
        for n in range(3000):
            base = f"{n:09d}"
            soma1 = sum(int(c) * p for c, p in zip(base, range(9, 0, -1)))
            if soma1 % 11 >= 10:
                dv = calcular_digitos(base)
                self.assertEqual(dv[0], "0")
                soma2 = sum(int(c) * p for c, p in zip(base, range(1, 10)))
                esperado = (soma2 % 11 - 2) % 11
                self.assertEqual(int(dv[1]), 0 if esperado >= 10 else esperado)
                achados += 1
        self.assertGreater(achados, 0)

    def test_invalidos(self) -> None:
        for cnh in ("02650306462", "02650306471", "11111111111", "00000000000", "", "0265030646", "026503064611", "abcdefghijk"):
            with self.subTest(cnh=cnh):
                self.assertFalse(validar_cnh(cnh))

    def test_gerar_valido(self) -> None:
        for base in ("123456789", "987654321", "000000001", "111111112"):
            self.assertTrue(validar_cnh(gerar_cnh(base)), base)
        self.assertEqual(gerar_cnh("026503064"), "02650306461")
        self.assertEqual(gerar_cnh("123456789"), "12345678900")

    def test_normalizar_e_erro(self) -> None:
        self.assertEqual(normalizar_cnh("026.503.064-61"), "02650306461")
        with self.assertRaises(ValueError):
            calcular_digitos("12")


if __name__ == "__main__":
    unittest.main()
