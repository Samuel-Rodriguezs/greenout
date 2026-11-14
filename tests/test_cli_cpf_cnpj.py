import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from cli_cpf_cnpj import main, validar_cnpj, validar_cpf


def rodar(args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(args)
    return code, buf.getvalue().strip().splitlines()


class TestCliCpfCnpj(unittest.TestCase):
    def test_cpf(self):
        self.assertTrue(validar_cpf("529.982.247-25"))
        self.assertFalse(validar_cpf("529.982.247-24"))
        self.assertFalse(validar_cpf("111.111.111-11"))

    def test_cnpj(self):
        self.assertTrue(validar_cnpj("11.222.333/0001-81"))
        self.assertFalse(validar_cnpj("11.222.333/0001-82"))
        self.assertFalse(validar_cnpj("00000000000000"))

    def test_main_valido(self):
        self.assertEqual(rodar(["529.982.247-25", "11222333000181"]),
                         (0, ["529.982.247-25: CPF válido", "11222333000181: CNPJ válido"]))

    def test_main_invalido(self):
        code, linhas = rodar(["123", "52998224724"])
        self.assertEqual(code, 1)
        self.assertEqual(linhas, ["123: ? inválido", "52998224724: CPF inválido"])


if __name__ == "__main__":
    unittest.main()
