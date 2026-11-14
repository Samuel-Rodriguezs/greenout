import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_bank_ocr import checksum_valido, classificar, ler_conta, renderizar

TODOS_UM = [
    "                           ",
    "  |  |  |  |  |  |  |  |  |",
    "  |  |  |  |  |  |  |  |  |",
]
UM_A_NOVE = [
    "    _  _     _  _  _  _  _ ",
    "  | _| _||_||_ |_   ||_||_|",
    "  ||_  _|  | _||_|  ||_| _|",
]


class TestKataBankOcr(unittest.TestCase):
    def test_todos_um(self):
        self.assertEqual(ler_conta(TODOS_UM), "111111111")

    def test_um_a_nove(self):
        self.assertEqual(ler_conta(UM_A_NOVE), "123456789")

    def test_zeros(self):
        linhas = [" _ " * 9, "| |" * 9, "|_|" * 9]
        self.assertEqual(ler_conta(linhas), "000000000")

    def test_ilegivel(self):
        linhas = list(UM_A_NOVE)
        linhas[0] = "X" + linhas[0][1:]
        conta = ler_conta(linhas)
        self.assertEqual(conta[0], "?")
        self.assertTrue(classificar(conta).endswith("ILL"))

    def test_checksum(self):
        self.assertTrue(checksum_valido("345882865"))
        self.assertTrue(checksum_valido("457508000"))
        self.assertFalse(checksum_valido("664371495"))
        self.assertFalse(checksum_valido("12345"))
        self.assertFalse(checksum_valido("12345678?"))

    def test_classificar(self):
        self.assertEqual(classificar("345882865"), "345882865")
        self.assertEqual(classificar("664371495"), "664371495 ERR")
        self.assertEqual(classificar("86110??36"), "86110??36 ILL")

    def test_renderizar_ida_e_volta(self):
        self.assertEqual(renderizar("123456789"), UM_A_NOVE)
        self.assertEqual(ler_conta(renderizar("345882865")), "345882865")

    def test_entrada_invalida(self):
        with self.assertRaises(ValueError):
            ler_conta(["abc"])
        with self.assertRaises(ValueError):
            renderizar("12a")


if __name__ == "__main__":
    unittest.main()
