import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from crip_checksum import (
    iban_digitos_controle, iban_valido, isbn10_para_13, isbn10_valido, isbn13_valido, luhn_digito, luhn_valido,
)


class TestChecksum(unittest.TestCase):
    def test_luhn(self):
        self.assertTrue(luhn_valido("79927398713"))
        self.assertTrue(luhn_valido("4539 1488 0343 6467"))
        self.assertTrue(luhn_valido("4111-1111-1111-1111"))
        self.assertFalse(luhn_valido("79927398710"))
        for ruim in ("", "0", "abc", "12a4"):
            self.assertFalse(luhn_valido(ruim))

    def test_luhn_digito(self):
        self.assertEqual(luhn_digito("7992739871"), 3)
        self.assertEqual(luhn_digito("411111111111111"), 1)
        with self.assertRaises(ValueError):
            luhn_digito("12x")

    def test_isbn10(self):
        self.assertTrue(isbn10_valido("0-306-40615-2"))
        self.assertTrue(isbn10_valido("080442957X"))
        self.assertFalse(isbn10_valido("0306406153"))
        self.assertFalse(isbn10_valido("03064061"))
        self.assertFalse(isbn10_valido("X306406152"))

    def test_isbn13(self):
        self.assertTrue(isbn13_valido("978-0-306-40615-7"))
        self.assertFalse(isbn13_valido("9780306406158"))
        self.assertFalse(isbn13_valido("978030640615"))

    def test_conversao(self):
        self.assertEqual(isbn10_para_13("0-306-40615-2"), "9780306406157")
        self.assertTrue(isbn13_valido(isbn10_para_13("080442957X")))
        with self.assertRaises(ValueError):
            isbn10_para_13("0306406153")

    def test_iban(self):
        for ok in ("GB82 WEST 1234 5698 7654 32", "DE89370400440532013000", "BR1800360305000010009795493C1"):
            self.assertTrue(iban_valido(ok), ok)
        for ruim in ("GB82WEST12345698765433", "GB82", "1234567890123456", "GB82WEST1234569876543!"):
            self.assertFalse(iban_valido(ruim), ruim)

    def test_iban_controle(self):
        self.assertEqual(iban_digitos_controle("GB", "WEST12345698765432"), "82")
        self.assertEqual(iban_digitos_controle("DE", "370400440532013000"), "89")
        self.assertEqual(iban_digitos_controle("BR", "00360305000010009795493C1"), "18")


if __name__ == "__main__":
    unittest.main()
