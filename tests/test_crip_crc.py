import os
import sys
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from crip_crc import adler32, crc32


class TestCrc(unittest.TestCase):
    def test_vetores(self):
        self.assertEqual(crc32(b"123456789"), 0xCBF43926)
        self.assertEqual(crc32(b""), 0)
        self.assertEqual(adler32(b"Wikipedia"), 0x11E60398)
        self.assertEqual(adler32(b""), 1)

    def test_contra_zlib(self):
        d = os.urandom(5000)
        self.assertEqual(crc32(d), zlib.crc32(d))
        self.assertEqual(adler32(d), zlib.adler32(d))

    def test_incremental(self):
        d = os.urandom(100)
        self.assertEqual(crc32(d[50:], crc32(d[:50])), crc32(d))
        self.assertEqual(adler32(d[50:], adler32(d[:50])), adler32(d))


if __name__ == "__main__":
    unittest.main()
