import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from camel_snake import camel_para_snake, snake_para_camel


class TestCamelSnake(unittest.TestCase):
    def test_camel_para_snake(self):
        self.assertEqual(camel_para_snake("meuNomeCompleto"), "meu_nome_completo")

    def test_pascal_case(self):
        self.assertEqual(camel_para_snake("MeuNome"), "meu_nome")

    def test_siglas_e_digitos(self):
        self.assertEqual(camel_para_snake("parseHTTPResponse"), "parse_http_response")
        self.assertEqual(camel_para_snake("valor2Final"), "valor2_final")

    def test_ja_minusculo_e_vazio(self):
        self.assertEqual(camel_para_snake("nome"), "nome")
        self.assertEqual(camel_para_snake(""), "")

    def test_snake_para_camel(self):
        self.assertEqual(snake_para_camel("meu_nome_completo"), "meuNomeCompleto")

    def test_snake_underscores_extras(self):
        self.assertEqual(snake_para_camel("_meu__nome_"), "meuNome")
        self.assertEqual(snake_para_camel("___"), "")

    def test_ida_e_volta(self):
        self.assertEqual(snake_para_camel(camel_para_snake("outroNomeLongo")), "outroNomeLongo")


if __name__ == "__main__":
    unittest.main()
