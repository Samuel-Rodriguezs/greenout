import hashlib
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from crip_sha256 import H0, K, sha256_hex


class TestSha256(unittest.TestCase):
    def test_constantes(self):
        self.assertEqual(K[0], 0x428A2F98)
        self.assertEqual(K[63], 0xC67178F2)
        self.assertEqual(H0[0], 0x6A09E667)
        self.assertEqual(H0[7], 0x5BE0CD19)

    def test_vetores_oficiais(self):
        self.assertEqual(sha256_hex(b""), "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        self.assertEqual(sha256_hex(b"abc"), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
        self.assertEqual(
            sha256_hex(b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq"),
            "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1",
        )

    def test_milhao_de_a(self):
        self.assertEqual(
            sha256_hex(b"a" * 1000000),
            "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0",
        )

    def test_contra_hashlib_bordas(self):
        for n in (55, 56, 57, 63, 64, 65, 119, 120, 128):
            d = os.urandom(n)
            self.assertEqual(sha256_hex(d), hashlib.sha256(d).hexdigest())


if __name__ == "__main__":
    unittest.main()
