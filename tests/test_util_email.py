import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from util_email import dominio_do_email, validar_email


class TestEmail(unittest.TestCase):
    def test_validos(self):
        for e in ["ana@exemplo.com", "a.b+tag@sub.dominio.com.br", "x_y-z@ex.io"]:
            with self.subTest(e=e):
                self.assertTrue(validar_email(e))

    def test_invalidos(self):
        for e in ["", "ana", "ana@", "@exemplo.com", "ana@exemplo", "ana@exemplo.c",
                  "ana@@exemplo.com", "a..b@exemplo.com", ".ana@exemplo.com",
                  "ana.@exemplo.com", "ana @exemplo.com", "ana@-exemplo.com"]:
            with self.subTest(e=e):
                self.assertFalse(validar_email(e))

    def test_tipo_e_tamanho(self):
        self.assertFalse(validar_email(None))
        self.assertFalse(validar_email("a" * 250 + "@ex.com"))

    def test_dominio(self):
        self.assertEqual(dominio_do_email("Ana@Exemplo.COM"), "exemplo.com")
        with self.assertRaises(ValueError):
            dominio_do_email("invalido")


if __name__ == "__main__":
    unittest.main()
