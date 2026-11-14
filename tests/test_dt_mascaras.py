import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dt_mascaras import (
    mascarar_cep,
    mascarar_cnpj,
    mascarar_cpf,
    mascarar_documento,
    mascarar_telefone,
    ocultar_cpf,
    so_digitos,
)


class TestMascaras(unittest.TestCase):
    def test_cpf(self) -> None:
        self.assertEqual(mascarar_cpf("12345678901"), "123.456.789-01")
        self.assertEqual(mascarar_cpf("123.456.789-01"), "123.456.789-01")
        with self.assertRaises(ValueError):
            mascarar_cpf("123")

    def test_cnpj(self) -> None:
        self.assertEqual(mascarar_cnpj("11222333000181"), "11.222.333/0001-81")
        with self.assertRaises(ValueError):
            mascarar_cnpj("1122233300018")

    def test_cep(self) -> None:
        self.assertEqual(mascarar_cep("01310100"), "01310-100")
        with self.assertRaises(ValueError):
            mascarar_cep("0131010")

    def test_telefone(self) -> None:
        self.assertEqual(mascarar_telefone("11912345678"), "(11) 91234-5678")
        self.assertEqual(mascarar_telefone("1132345678"), "(11) 3234-5678")
        self.assertEqual(mascarar_telefone("+55 11 91234-5678"), "+55 (11) 91234-5678")
        self.assertEqual(mascarar_telefone("551132345678"), "+55 (11) 3234-5678")
        self.assertEqual(mascarar_telefone("55991234567"), "(55) 99123-4567")  # DDD 55 (RS)

    def test_telefone_invalido(self) -> None:
        for t in ("", "123456789", "0112345678", "10912345678", "123456789012345"):
            with self.subTest(t=t):
                with self.assertRaises(ValueError):
                    mascarar_telefone(t)

    def test_documento(self) -> None:
        self.assertEqual(mascarar_documento("12345678901"), "123.456.789-01")
        self.assertEqual(mascarar_documento("11222333000181"), "11.222.333/0001-81")
        with self.assertRaises(ValueError):
            mascarar_documento("123")

    def test_ocultar_cpf(self) -> None:
        self.assertEqual(ocultar_cpf("123.456.789-01"), "***.456.789-**")

    def test_so_digitos_e_idempotencia(self) -> None:
        self.assertEqual(so_digitos("(11) 9-1234_5678"), "11912345678")
        masc = mascarar_cpf("12345678901")
        self.assertEqual(mascarar_cpf(masc), masc)


if __name__ == "__main__":
    unittest.main()
