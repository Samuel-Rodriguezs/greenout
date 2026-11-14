import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from proj_ini import parse_ini, converter, ErroIni

EXEMPLO = """
; comentario
nome = global
[servidor]
porta = 8080
debug = true
taxa=0.5
titulo = "ola mundo"
# outro comentario
[vazio]
"""


class TestIni(unittest.TestCase):
    def test_parse_completo(self):
        c = parse_ini(EXEMPLO)
        self.assertEqual(c[""], {"nome": "global"})
        self.assertEqual(
            c["servidor"],
            {"porta": 8080, "debug": True, "taxa": 0.5, "titulo": "ola mundo"},
        )
        self.assertEqual(c["vazio"], {})

    def test_sem_chaves_globais(self):
        self.assertNotIn("", parse_ini("[a]\nx=1"))

    def test_converter(self):
        self.assertIs(converter("off"), False)
        self.assertEqual(converter("-3"), -3)
        self.assertEqual(converter("abc"), "abc")

    def test_valor_com_igual(self):
        self.assertEqual(parse_ini("[a]\nurl=x?y=1")["a"]["url"], "x?y=1")

    def test_erros(self):
        for texto in ("[abc", "sem igual", "[a]\n=1", "[]"):
            with self.subTest(texto=texto):
                with self.assertRaises(ErroIni):
                    parse_ini(texto)


if __name__ == "__main__":
    unittest.main()
