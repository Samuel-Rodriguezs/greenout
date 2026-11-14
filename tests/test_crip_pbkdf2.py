import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from crip_pbkdf2 import pbkdf2


class TestPbkdf2(unittest.TestCase):
    def test_rfc6070_sha1(self):
        self.assertEqual(pbkdf2(b"password", b"salt", 1, 20, "sha1").hex(), "0c60c80f961f0e71f3a9b524af6012062fe037a6")
        self.assertEqual(pbkdf2(b"password", b"salt", 2, 20, "sha1").hex(), "ea6c014dc72d6f8ccd1ed92ace1d41f0d8de8957")
        self.assertEqual(pbkdf2(b"password", b"salt", 4096, 20, "sha1").hex(), "4b007901b765489abead49d926f721d065a429c1")

    def test_contra_hashlib_multibloco(self):
        for alg in ("sha256", "sha512"):
            self.assertEqual(
                pbkdf2(b"senha", b"sal", 50, 100, alg),
                hashlib.pbkdf2_hmac(alg, b"senha", b"sal", 50, 100),
            )

    def test_invalido(self):
        with self.assertRaises(ValueError):
            pbkdf2(b"a", b"b", 0, 10)


if __name__ == "__main__":
    unittest.main()
