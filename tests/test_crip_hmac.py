import hmac
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from crip_hmac import comparar_constante, hmac_digest, verificar


class TestHmac(unittest.TestCase):
    def test_rfc4231_caso2(self):
        d = hmac_digest(b"Jefe", b"what do ya want for nothing?")
        self.assertEqual(d.hex(), "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843")

    def test_contra_hmac(self):
        for tam in (0, 5, 64, 65, 200):
            k, m = os.urandom(tam), os.urandom(77)
            for alg in ("sha256", "sha1", "md5", "sha512"):
                self.assertEqual(hmac_digest(k, m, alg), hmac.new(k, m, alg).digest())

    def test_verificar(self):
        tag = hmac_digest(b"k", b"m")
        self.assertTrue(verificar(b"k", b"m", tag))
        self.assertFalse(verificar(b"k", b"x", tag))
        self.assertFalse(verificar(b"k", b"m", tag[:-1]))
        self.assertFalse(comparar_constante(b"a", b"ab"))


if __name__ == "__main__":
    unittest.main()
