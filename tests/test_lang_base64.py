import base64
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from lang_base64 import ErroBase64, codificar, decodificar


class TestBase64(unittest.TestCase):
    def test_vetores_rfc4648(self):
        casos = {b"": "", b"f": "Zg==", b"fo": "Zm8=", b"foo": "Zm9v",
                 b"foob": "Zm9vYg==", b"fooba": "Zm9vYmE=", b"foobar": "Zm9vYmFy"}
        for bruto, cod in casos.items():
            self.assertEqual(codificar(bruto), cod)
            self.assertEqual(decodificar(cod), bruto)

    def test_concordancia_com_stdlib(self):
        for n in range(0, 40):
            dados = os.urandom(n)
            self.assertEqual(codificar(dados), base64.b64encode(dados).decode())
            self.assertEqual(codificar(dados, url_safe=True), base64.urlsafe_b64encode(dados).decode())
            self.assertEqual(decodificar(base64.b64encode(dados).decode()), dados)

    def test_url_safe(self):
        dados = bytes([0xFB, 0xFF, 0xBF])
        self.assertEqual(codificar(dados), "+/+/")
        self.assertEqual(codificar(dados, url_safe=True), "-_-_")
        self.assertEqual(decodificar("-_-_", url_safe=True), dados)

    def test_sem_preenchimento(self):
        self.assertEqual(codificar(b"fo", preenchimento=False), "Zm8")
        self.assertEqual(decodificar("Zm8"), b"fo")

    def test_ignora_espacos(self):
        self.assertEqual(decodificar("Zm9v\nYmFy "), b"foobar")

    def test_utf8(self):
        s = "ação ✓".encode("utf-8")
        self.assertEqual(decodificar(codificar(s)), s)

    def test_erros(self):
        for t in ["Z", "Zm9v!", "Zg=", "Zg===", "Z=g=", "Zm9vY"]:
            with self.assertRaises(ErroBase64, msg=t):
                decodificar(t)


if __name__ == "__main__":
    unittest.main()
