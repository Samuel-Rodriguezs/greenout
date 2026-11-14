import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dt_titulo_eleitor import calcular_digitos, gerar_titulo, uf_do_titulo, validar_titulo


class TestTituloEleitor(unittest.TestCase):
    def test_calculo_manual(self) -> None:
        # inscrição 12345678, UF 01: soma1 = 1*2+2*3+3*4+4*5+5*6+6*7+7*8+8*9 = 240; 240%11 = 9
        # soma2 = 0*7 + 1*8 + 9*9 = 89; 89 % 11 = 1
        self.assertEqual(calcular_digitos("1234567801"), "91")
        self.assertTrue(validar_titulo("123456780191"))
        self.assertTrue(validar_titulo("1234 5678 0191"))

    def test_resto_dez_vira_zero(self) -> None:
        # varre inscrições até achar casos em que o resto da primeira soma é 10
        achados = 0
        for n in range(2000):
            base = f"{n:08d}06"
            soma1 = sum(int(base[i]) * (i + 2) for i in range(8))
            if soma1 % 11 == 10:
                self.assertEqual(calcular_digitos(base)[0], "0")
                achados += 1
        self.assertGreater(achados, 0)

    def test_excecao_sp_mg_resto_zero(self) -> None:
        # inscrição 00000000: soma1 = 0 => resto 0
        self.assertEqual(calcular_digitos("0000000001")[0], "1")  # SP
        self.assertEqual(calcular_digitos("0000000002")[0], "1")  # MG
        self.assertEqual(calcular_digitos("0000000003")[0], "0")  # RJ

    def test_gerar_sempre_valido(self) -> None:
        for uf in range(1, 29):
            for insc in ("00000000", "12345678", "99999999", "40506070"):
                self.assertTrue(validar_titulo(gerar_titulo(insc, uf)), (insc, uf))

    def test_dv_alterado_invalida(self) -> None:
        t = gerar_titulo("12345678", 3)
        for i in range(10):
            alterado = t[:11] + str(i)
            self.assertEqual(validar_titulo(alterado), alterado == t)

    def test_invalidos(self) -> None:
        for t in ("", "12345678019", "1234567801911", "123456782991", "abcdefghijkl"):
            with self.subTest(t=t):
                self.assertFalse(validar_titulo(t))

    def test_uf(self) -> None:
        self.assertEqual(uf_do_titulo(gerar_titulo("12345678", 1)), "SP")
        self.assertEqual(uf_do_titulo(gerar_titulo("12345678", 28)), "ZZ")
        with self.assertRaises(ValueError):
            uf_do_titulo("123")

    def test_erros_de_geracao(self) -> None:
        with self.assertRaises(ValueError):
            gerar_titulo("123", 1)
        with self.assertRaises(ValueError):
            gerar_titulo("12345678", 29)
        with self.assertRaises(ValueError):
            calcular_digitos("12")


if __name__ == "__main__":
    unittest.main()
