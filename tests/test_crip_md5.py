import hashlib
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from crip_md5 import md5_hex


class TestMd5(unittest.TestCase):
    def test_vetores_rfc1321(self):
        casos = {
            b"": "d41d8cd98f00b204e9800998ecf8427e",
            b"a": "0cc175b9c0f1b6a831c399e269772661",
            b"abc": "900150983cd24fb0d6963f7d28e17f72",
            b"message digest": "f96b697d7cb7938d525a2f31aaf161d0",
            b"abcdefghijklmnopqrstuvwxyz": "c3fcd3d76192e4007dfb496cca67e13b",
            b"12345678901234567890123456789012345678901234567890123456789012345678901234567890": "57edf4a22be3c955ac49da2e2107b67a",
        }
        for entrada, esperado in casos.items():
            self.assertEqual(md5_hex(entrada), esperado)

    def test_contra_hashlib(self):
        for n in (0, 55, 56, 63, 64, 65, 1000):
            d = os.urandom(n)
            self.assertEqual(md5_hex(d), hashlib.md5(d).hexdigest())


if __name__ == "__main__":
    unittest.main()
