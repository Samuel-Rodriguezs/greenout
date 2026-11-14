import base64
import binascii
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from crip_base64url import (
    b64_codificar, b64_decodificar, b64url_codificar, b64url_decodificar, hexlify, unhexlify,
)


class TestBase64Url(unittest.TestCase):
    def test_rfc4648(self):
        casos = {b"": "", b"f": "Zg==", b"fo": "Zm8=", b"foo": "Zm9v", b"foob": "Zm9vYg==", b"fooba": "Zm9vYmE=", b"foobar": "Zm9vYmFy"}
        for b, s in casos.items():
            self.assertEqual(b64_codificar(b), s)
            self.assertEqual(b64_decodificar(s), b)
            self.assertEqual(b64_decodificar(s.rstrip("=")), b)

    def test_contra_stdlib(self):
        for n in range(0, 40):
            d = os.urandom(n)
            self.assertEqual(b64_codificar(d), base64.b64encode(d).decode())
            self.assertEqual(b64url_codificar(d, True), base64.urlsafe_b64encode(d).decode())
            self.assertEqual(b64url_decodificar(b64url_codificar(d)), d)
            self.assertEqual(hexlify(d), binascii.hexlify(d).decode())
            self.assertEqual(unhexlify(hexlify(d)), d)

    def test_url_sem_padding_e_alfabeto(self):
        self.assertEqual(b64url_codificar(b"\xfb\xff\xfe"), "-__-")
        self.assertEqual(b64_codificar(b"\xfb\xff\xfe"), "+//+")
        self.assertNotIn("=", b64url_codificar(b"f"))

    def test_invalidos(self):
        for s in ("Z", "ab$d", "Zm9v Yg"):
            with self.assertRaises(ValueError):
                b64_decodificar(s)
        with self.assertRaises(ValueError):
            b64_decodificar("-_-_")  # alfabeto URL no decodificador padrão
        for h in ("abc", "zz", "0x"):
            with self.assertRaises(ValueError):
                unhexlify(h)

    def test_hex_maiusculo(self):
        self.assertEqual(unhexlify("DEADbeef"), b"\xde\xad\xbe\xef")


if __name__ == "__main__":
    unittest.main()
