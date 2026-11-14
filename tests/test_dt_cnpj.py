import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dt_cnpj import calcular_digitos, formatar_cnpj, gerar_cnpj, normalizar, validar_cnpj


class TestCnpj(unittest.TestCase):
    def test_validos_conhecidos(self) -> None:
        for cnpj in ("11.222.333/0001-81", "11222333000181", "00.000.000/0001-91", "33.000.167/0001-01"):
            with self.subTest(cnpj=cnpj):
                self.assertTrue(validar_cnpj(cnpj))

    def test_alfanumerico_oficial(self) -> None:
        self.assertTrue(validar_cnpj("12.ABC.345/01DE-35"))
        self.assertFalse(validar_cnpj("12.ABC.345/01DE-36"))
        self.assertEqual(calcular_digitos("12ABC34501DE"), "35")

    def test_invalidos(self) -> None:
        for cnpj in ("11.222.333/0001-82", "11222333000180", "00000000000000", "11111111111111",
                     "1122233300018", "112223330001811", "", "11.222.333/0001-8A", "ab"):
            with self.subTest(cnpj=cnpj):
                self.assertFalse(validar_cnpj(cnpj))

    def test_digito_trocado_sempre_invalida(self) -> None:
        base = "112223330001"
        correto = gerar_cnpj(base)
        for i in range(10):
            alterado = correto[:13] + str(i)
            self.assertEqual(validar_cnpj(alterado), alterado == correto)

    def test_gerar_e_formatar(self) -> None:
        self.assertEqual(gerar_cnpj("112223330001"), "11222333000181")
        self.assertEqual(formatar_cnpj("11222333000181"), "11.222.333/0001-81")
        self.assertEqual(formatar_cnpj("12abc34501de35"), "12.ABC.345/01DE-35")
        with self.assertRaises(ValueError):
            formatar_cnpj("123")

    def test_normalizar(self) -> None:
        self.assertEqual(normalizar(" 11.222.333/0001-81 "), "11222333000181")

    def test_base_invalida(self) -> None:
        with self.assertRaises(ValueError):
            calcular_digitos("123")


if __name__ == "__main__":
    unittest.main()
