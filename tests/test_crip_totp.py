import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from crip_totp import chave_de_base32, hotp, totp, uri_provisionamento, verificar_totp

SEGREDO = b"12345678901234567890"


class TestTotp(unittest.TestCase):
    def test_hotp_rfc4226(self):
        esperado = ["755224", "287082", "359152", "969429", "338314", "254676", "287922", "162583", "399871", "520489"]
        self.assertEqual([hotp(SEGREDO, i) for i in range(10)], esperado)

    def test_totp_rfc6238_sha1(self):
        casos = {59: "94287082", 1111111109: "07081804", 1111111111: "14050471", 1234567890: "89005924", 2000000000: "69279037"}
        for t, cod in casos.items():
            self.assertEqual(totp(SEGREDO, t, digitos=8), cod)

    def test_totp_rfc6238_sha256_sha512(self):
        self.assertEqual(totp(b"12345678901234567890123456789012", 59, digitos=8, algoritmo="sha256"), "46119246")
        self.assertEqual(
            totp(b"1234567890123456789012345678901234567890123456789012345678901234", 59, digitos=8, algoritmo="sha512"),
            "90693936",
        )

    def test_verificar_janela(self):
        cod = totp(SEGREDO, 1000)
        self.assertTrue(verificar_totp(cod, SEGREDO, 1000))
        self.assertTrue(verificar_totp(cod, SEGREDO, 1030))
        self.assertFalse(verificar_totp(cod, SEGREDO, 1100))

    def test_digitos_invalidos(self):
        with self.assertRaises(ValueError):
            hotp(SEGREDO, 0, 10)

    def test_base32_e_uri(self):
        self.assertEqual(chave_de_base32("GEZD GNBV GY3T QOJQ GEZD GNBV GY3T QOJQ"), SEGREDO)
        uri = uri_provisionamento(SEGREDO, "ana@ex.com", "Lab")
        self.assertTrue(uri.startswith("otpauth://totp/Lab:ana%40ex.com?secret=GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"))


if __name__ == "__main__":
    unittest.main()
