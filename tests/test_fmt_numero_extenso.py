import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fmt_numero_extenso import ErroNumero, de_extenso, para_extenso

CASOS = {
    0: "zero", 1: "um", 15: "quinze", 21: "vinte e um", 99: "noventa e nove", 100: "cem",
    101: "cento e um", 110: "cento e dez", 200: "duzentos", 345: "trezentos e quarenta e cinco",
    1000: "mil", 1001: "mil e um", 1100: "mil e cem", 1234: "mil duzentos e trinta e quatro",
    2000: "dois mil", 2500: "dois mil e quinhentos", 21000: "vinte e um mil",
    100000: "cem mil", 1000000: "um milhão", 2000000: "dois milhões",
    2500000: "dois milhões e quinhentos mil", 1000001: "um milhão e um",
    3000000000: "três bilhões", -7: "menos sete",
}


class TestFmtNumeroExtenso(unittest.TestCase):
    def test_para_extenso(self):
        for n, texto in CASOS.items():
            with self.subTest(n=n):
                self.assertEqual(para_extenso(n), texto)

    def test_de_extenso(self):
        for n, texto in CASOS.items():
            with self.subTest(texto=texto):
                self.assertEqual(de_extenso(texto), n)

    def test_variacoes_aceitas(self):
        self.assertEqual(de_extenso("Vinte E Dois"), 22)
        self.assertEqual(de_extenso("duas mil e duzentas"), 2200)
        self.assertEqual(de_extenso("dois mil duzentos"), 2200)
        self.assertEqual(de_extenso("vinte-e-três"), 23)
        self.assertEqual(de_extenso("tres"), 3)
        self.assertEqual(de_extenso("dezasseis"), 16)
        self.assertEqual(de_extenso("mil e quinhentos"), 1500)

    def test_ida_e_volta(self):
        for n in list(range(0, 2200)) + [10**6 + 5, 123456789, 999999999999, -1234]:
            self.assertEqual(de_extenso(para_extenso(n)), n)

    def test_malformados(self):
        for ruim in ["", "e", "menos", "vinte trinta", "um dois", "vinte e dez", "banana", "cem e um",
                     "mil mil", "e um", "um e", "um milhões", "dois milhão", "milhão", "zero um",
                     "cento cento", "um e e dois", "mil milhões", "dois e mil"]:
            with self.subTest(ruim=ruim):
                with self.assertRaises(ErroNumero):
                    de_extenso(ruim)
        for ruim in (10**15, 1.5, True):
            with self.assertRaises(ErroNumero):
                para_extenso(ruim)


if __name__ == "__main__":
    unittest.main()
