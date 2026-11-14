import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ds_csv_tipado import converter, inferir_tipo, ler_csv


class TestCsvTipado(unittest.TestCase):
    def test_inferir(self):
        self.assertEqual(inferir_tipo(["1", "2", ""]), "int")
        self.assertEqual(inferir_tipo(["1", "2.5"]), "float")
        self.assertEqual(inferir_tipo(["sim", "não"]), "bool")
        self.assertEqual(inferir_tipo(["2024-01-31"]), "date")
        self.assertEqual(inferir_tipo(["2024-13-01"]), "str")
        self.assertEqual(inferir_tipo(["a", "1"]), "str")
        self.assertEqual(inferir_tipo([]), "str")

    def test_ler_inferido(self):
        txt = "nome,idade,nota,ativo,nasc\nAna,30,8.5,true,1994-05-01\nBia,,7,false,\n"
        r = ler_csv(txt)
        self.assertEqual(r[0], {"nome": "Ana", "idade": 30, "nota": 8.5, "ativo": True, "nasc": date(1994, 5, 1)})
        self.assertEqual(r[1], {"nome": "Bia", "idade": None, "nota": 7.0, "ativo": False, "nasc": None})

    def test_decimal_virgula_e_separador(self):
        r = ler_csv("p;v\nx;1.234,56\ny;2,5\n", sep=";", decimal=",")
        self.assertAlmostEqual(r[0]["v"], 1234.56)
        self.assertAlmostEqual(r[1]["v"], 2.5)

    def test_esquema_forca_tipo(self):
        r = ler_csv("cod\n007\n", esquema={"cod": "str"})
        self.assertEqual(r[0]["cod"], "007")

    def test_erro_com_linha(self):
        with self.assertRaises(ValueError) as c:
            ler_csv("a\n1\nx\n", esquema={"a": "int"})
        self.assertIn("linha 3", str(c.exception))

    def test_colunas_inconsistentes(self):
        with self.assertRaises(ValueError):
            ler_csv("a,b\n1\n")

    def test_campo_com_aspas(self):
        r = ler_csv('n,t\n1,"a, b"\n')
        self.assertEqual(r[0]["t"], "a, b")

    def test_converter_tipo_invalido(self):
        with self.assertRaises(ValueError):
            converter("1", "xyz")

    def test_vazio(self):
        self.assertEqual(ler_csv(""), [])


if __name__ == "__main__":
    unittest.main()
