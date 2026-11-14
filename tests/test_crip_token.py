import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from crip_token import (
    ALFABETO_SEM_AMBIGUOS, codigo_numerico, entropia_bits, token_alfabeto, token_hex, token_urlsafe,
)


class TestToken(unittest.TestCase):
    def test_hex(self):
        t = token_hex(8)
        self.assertRegex(t, r"^[0-9a-f]{16}$")
        self.assertNotEqual(token_hex(16), token_hex(16))

    def test_urlsafe(self):
        self.assertRegex(token_urlsafe(32), r"^[A-Za-z0-9_-]+$")

    def test_alfabeto(self):
        t = token_alfabeto(200, "ab")
        self.assertEqual(len(t), 200)
        self.assertEqual(set(t), {"a", "b"})
        self.assertIsNone(re.search(r"[0O1lI]", token_alfabeto(300, ALFABETO_SEM_AMBIGUOS)))

    def test_codigo_numerico_zeros(self):
        for _ in range(50):
            c = codigo_numerico(6)
            self.assertEqual(len(c), 6)
            self.assertTrue(c.isdigit())

    def test_entropia(self):
        self.assertAlmostEqual(entropia_bits(10, "01"), 10.0)
        self.assertAlmostEqual(entropia_bits(4, "0123456789"), 13.2877, places=3)

    def test_erros(self):
        for f in (token_hex, token_urlsafe, codigo_numerico):
            with self.assertRaises(ValueError):
                f(0)
        with self.assertRaises(ValueError):
            token_alfabeto(5, "aaa")


if __name__ == "__main__":
    unittest.main()
