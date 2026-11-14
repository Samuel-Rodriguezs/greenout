import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fmt_base58 import ErroBase58, codificar, codificar_check, decodificar, decodificar_check


class TestFmtBase58(unittest.TestCase):
    def test_vetores_conhecidos(self):
        casos = {b"": "", b"\x00": "1", b"\x00\x00": "11", b"a": "2g", b"abc": "ZiCa",
                 b"Hello World!": "2NEpo7TZRRrLZSi2U", b"\x00\x00\x28\x7f\xb4\xcd": "11233QC4"}
        for bruto, enc in casos.items():
            with self.subTest(enc=enc):
                self.assertEqual(codificar(bruto), enc)
                self.assertEqual(decodificar(enc), bruto)

    def test_ida_e_volta_aleatoria(self):
        for n in range(0, 50):
            d = os.urandom(n)
            self.assertEqual(decodificar(codificar(d)), d)
            self.assertEqual(decodificar_check(codificar_check(d)), d)

    def test_check_endereco_bitcoin(self):
        # endereço do bloco gênese: versão 0x00 + hash160
        end = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        bruto = decodificar_check(end)
        self.assertEqual(len(bruto), 21)
        self.assertEqual(bruto[0], 0)
        self.assertEqual(codificar_check(bruto), end)

    def test_malformados(self):
        for ruim in ["0", "O", "I", "l", "abc def", "é"]:
            with self.subTest(ruim=ruim):
                with self.assertRaises(ErroBase58):
                    decodificar(ruim)
        with self.assertRaises(ErroBase58):
            decodificar_check("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNb")
        with self.assertRaises(ErroBase58):
            decodificar_check("11")


if __name__ == "__main__":
    unittest.main()
