import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from util_cpf import formatar_cpf, validar_cpf


class TestCpf(unittest.TestCase):
    def test_valido_com_e_sem_mascara(self):
        self.assertTrue(validar_cpf("529.982.247-25"))
        self.assertTrue(validar_cpf("52998224725"))

    def test_digito_errado(self):
        self.assertFalse(validar_cpf("529.982.247-24"))

    def test_digitos_repetidos(self):
        self.assertFalse(validar_cpf("111.111.111-11"))
        self.assertFalse(validar_cpf("00000000000"))

    def test_tamanho_invalido(self):
        self.assertFalse(validar_cpf("1234567890"))
        self.assertFalse(validar_cpf("529982247250"))
        self.assertFalse(validar_cpf(""))

    def test_caracteres_invalidos_e_tipo(self):
        self.assertFalse(validar_cpf("529.982.247-2a"))
        self.assertFalse(validar_cpf(52998224725))

    def test_formatar(self):
        self.assertEqual(formatar_cpf("52998224725"), "529.982.247-25")
        with self.assertRaises(ValueError):
            formatar_cpf("123")


if __name__ == "__main__":
    unittest.main()
