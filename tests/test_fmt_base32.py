import base64
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fmt_base32 import ALFABETO_HEX, ErroBase32, codificar, decodificar


class TestFmtBase32(unittest.TestCase):
    def test_vetores_rfc4648(self):
        casos = {b"": "", b"f": "MY======", b"fo": "MZXQ====", b"foo": "MZXW6===",
                 b"foob": "MZXW6YQ=", b"fooba": "MZXW6YTB", b"foobar": "MZXW6YTBOI======"}
        for bruto, enc in casos.items():
            with self.subTest(bruto=bruto):
                self.assertEqual(codificar(bruto), enc)
                self.assertEqual(decodificar(enc), bruto)

    def test_hex_alfabeto(self):
        self.assertEqual(codificar(b"foobar", ALFABETO_HEX), "CPNMUOJ1E8======")
        self.assertEqual(decodificar("CPNMUOJ1E8======", ALFABETO_HEX), b"foobar")

    def test_sem_padding_e_minusculas(self):
        self.assertEqual(codificar(b"foo", padding=False), "MZXW6")
        self.assertEqual(decodificar("mzxw6"), b"foo")

    def test_confere_com_stdlib(self):
        for n in range(0, 40):
            dados = os.urandom(n)
            self.assertEqual(codificar(dados), base64.b32encode(dados).decode())
            self.assertEqual(decodificar(base64.b32encode(dados).decode()), dados)

    def test_malformados(self):
        for ruim in ["M", "MZXW6=", "MZ=XQ===", "MZXW6YQ1", "MY=======", "M!======", "MZ======", "MZXW 6==="]:
            with self.subTest(ruim=ruim):
                with self.assertRaises(ErroBase32):
                    decodificar(ruim)


if __name__ == "__main__":
    unittest.main()
