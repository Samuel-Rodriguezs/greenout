import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from rede_ipv6 import (compactar, compactar_valor, eh_link_local, eh_loopback,
                       expandir, parse_ipv6)


class TestRedeIPv6(unittest.TestCase):
    def test_expandir(self):
        self.assertEqual(expandir("::1"), "0000:0000:0000:0000:0000:0000:0000:0001")
        self.assertEqual(expandir("2001:db8::ff00:42:8329"),
                         "2001:0db8:0000:0000:0000:ff00:0042:8329")
        self.assertEqual(expandir("::"), ":".join(["0000"] * 8))
        self.assertEqual(expandir("1::"), "0001:" + ":".join(["0000"] * 7))

    def test_compactar(self):
        self.assertEqual(compactar("2001:0db8:0000:0000:0000:ff00:0042:8329"), "2001:db8::ff00:42:8329")
        self.assertEqual(compactar("0:0:0:0:0:0:0:0"), "::")
        self.assertEqual(compactar("0:0:0:0:0:0:0:1"), "::1")
        self.assertEqual(compactar("2001:db8:0:0:1:0:0:1"), "2001:db8::1:0:0:1")  # primeira sequência mais longa
        self.assertEqual(compactar("2001:db8:0:1:1:1:1:1"), "2001:db8:0:1:1:1:1:1")  # um zero só
        self.assertEqual(compactar("1:0:0:2:0:0:0:3"), "1:0:0:2::3")  # maior sequência vence
        self.assertEqual(compactar("FE80:0:0:0:0:0:0:0"), "fe80::")

    def test_ida_e_volta(self):
        for t in ["::", "::1", "fe80::1", "2001:db8:85a3::8a2e:370:7334", "1:2:3:4:5:6:7:8"]:
            self.assertEqual(compactar_valor(parse_ipv6(expandir(t))), compactar(t))

    def test_ipv4_embutido(self):
        self.assertEqual(parse_ipv6("::ffff:192.0.2.1"), 0xFFFFC0000201)

    def test_invalidos(self):
        for ruim in ["", "1::2::3", "1:2:3:4:5:6:7", "1:2:3:4:5:6:7:8:9", "g::1",
                     "12345::1", "1:2:3:4:5:6:7::8", ":::", "::ffff:1.2.3"]:
            with self.assertRaises(ValueError, msg=ruim):
                parse_ipv6(ruim)

    def test_tipos(self):
        self.assertTrue(eh_loopback("::1"))
        self.assertFalse(eh_loopback("::2"))
        self.assertTrue(eh_link_local("fe80::abcd"))
        self.assertTrue(eh_link_local("febf::1"))
        self.assertFalse(eh_link_local("fec0::1"))


if __name__ == "__main__":
    unittest.main()
