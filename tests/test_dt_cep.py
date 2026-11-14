import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dt_cep import eh_cep_unico, formatar_cep, normalizar_cep, regiao_postal, validar_cep


class TestCep(unittest.TestCase):
    def test_validos(self) -> None:
        for cep in ("01310-100", "01310100", " 70040-010 ", "99999-999"):
            with self.subTest(cep=cep):
                self.assertTrue(validar_cep(cep))

    def test_invalidos(self) -> None:
        for cep in ("", "1234567", "123456789", "12345-67", "1234-5678", "abcde-fgh", "00000-000", "12.345-678"):
            with self.subTest(cep=cep):
                self.assertFalse(validar_cep(cep))

    def test_normalizar_e_formatar(self) -> None:
        self.assertEqual(normalizar_cep("01310-100"), "01310100")
        self.assertEqual(formatar_cep("01310100"), "01310-100")
        self.assertEqual(formatar_cep("01310-100"), "01310-100")
        with self.assertRaises(ValueError):
            formatar_cep("123")

    def test_regiao(self) -> None:
        self.assertEqual(regiao_postal("01310-100"), "Grande São Paulo")
        self.assertEqual(regiao_postal("20040-020"), "Rio de Janeiro e Espírito Santo")
        self.assertEqual(regiao_postal("90010-000"), "Rio Grande do Sul")
        self.assertIn("Distrito Federal", regiao_postal("70040-010"))

    def test_cep_unico(self) -> None:
        self.assertTrue(eh_cep_unico("69900-000"))
        self.assertFalse(eh_cep_unico("01310-100"))


if __name__ == "__main__":
    unittest.main()
