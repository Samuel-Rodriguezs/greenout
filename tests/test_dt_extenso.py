import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dt_extenso import numero_por_extenso, reais_por_extenso


class TestExtenso(unittest.TestCase):
    def test_basicos(self) -> None:
        casos = {
            0: "zero", 1: "um", 10: "dez", 11: "onze", 19: "dezenove", 20: "vinte",
            21: "vinte e um", 99: "noventa e nove", 100: "cem", 101: "cento e um",
            110: "cento e dez", 200: "duzentos", 999: "novecentos e noventa e nove",
        }
        for n, esperado in casos.items():
            with self.subTest(n=n):
                self.assertEqual(numero_por_extenso(n), esperado)

    def test_milhares(self) -> None:
        casos = {
            1000: "mil", 1001: "mil e um", 1100: "mil e cem", 1101: "mil cento e um",
            1234: "mil duzentos e trinta e quatro", 2000: "dois mil", 2026: "dois mil e vinte e seis",
            10000: "dez mil", 100000: "cem mil", 100001: "cem mil e um",
            101000: "cento e um mil", 999999: "novecentos e noventa e nove mil novecentos e noventa e nove",
        }
        for n, esperado in casos.items():
            with self.subTest(n=n):
                self.assertEqual(numero_por_extenso(n), esperado)

    def test_milhoes_e_alem(self) -> None:
        casos = {
            1_000_000: "um milhão", 2_000_000: "dois milhões", 1_000_001: "um milhão e um",
            1_200_000: "um milhão e duzentos mil", 2_001_000: "dois milhões e mil",
            1_234_567: "um milhão duzentos e trinta e quatro mil quinhentos e sessenta e sete",
            1_000_000_000: "um bilhão", 3_000_000_000_000: "três trilhões",
            1_100_000: "um milhão e cem mil",
        }
        for n, esperado in casos.items():
            with self.subTest(n=n):
                self.assertEqual(numero_por_extenso(n), esperado)

    def test_negativo_e_limite(self) -> None:
        self.assertEqual(numero_por_extenso(-42), "menos quarenta e dois")
        with self.assertRaises(ValueError):
            numero_por_extenso(10**15)

    def test_feminino(self) -> None:
        self.assertEqual(numero_por_extenso(1, feminino=True), "uma")
        self.assertEqual(numero_por_extenso(2, feminino=True), "duas")
        self.assertEqual(numero_por_extenso(200, feminino=True), "duzentas")
        self.assertEqual(numero_por_extenso(2000, feminino=True), "duas mil")
        self.assertEqual(numero_por_extenso(21, feminino=True), "vinte e uma")
        self.assertEqual(numero_por_extenso(1000, feminino=True), "mil")
        self.assertEqual(numero_por_extenso(2_000_000, feminino=True), "dois milhões")

    def test_reais(self) -> None:
        casos = {
            0: "zero reais", 1: "um real", 2: "dois reais", Decimal("0.01"): "um centavo",
            Decimal("0.50"): "cinquenta centavos", Decimal("1.01"): "um real e um centavo",
            "1.50": "um real e cinquenta centavos", 1234.56: "mil duzentos e trinta e quatro reais e cinquenta e seis centavos",
            1_000_000: "um milhão de reais", 2_000_000: "dois milhões de reais",
            Decimal("1000000.05"): "um milhão de reais e cinco centavos",
            1_000_001: "um milhão e um reais", -3: "menos três reais", 100: "cem reais",
        }
        for valor, esperado in casos.items():
            with self.subTest(valor=valor):
                self.assertEqual(reais_por_extenso(valor), esperado)

    def test_reais_arredondamento(self) -> None:
        self.assertEqual(reais_por_extenso(Decimal("0.005")), "um centavo")
        self.assertEqual(reais_por_extenso(Decimal("0.004")), "zero reais")
        self.assertEqual(reais_por_extenso(Decimal("1.999")), "dois reais")
        self.assertEqual(reais_por_extenso(0.1 + 0.2), "trinta centavos")


if __name__ == "__main__":
    unittest.main()
