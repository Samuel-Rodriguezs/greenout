import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from rede_mac import (eh_broadcast, eh_local, eh_multicast, eui64, formatar_mac,
                      link_local_ipv6, mac_de_eui64, oui, parse_mac)


class TestRedeMac(unittest.TestCase):
    def test_parse_formatos(self):
        esperado = 0x001A2B3C4D5E
        for t in ["00:1a:2b:3c:4d:5e", "00-1A-2B-3C-4D-5E", "001a.2b3c.4d5e", "001A2B3C4D5E"]:
            self.assertEqual(parse_mac(t), esperado, t)

    def test_formatar(self):
        self.assertEqual(formatar_mac(0x001A2B3C4D5E), "00:1a:2b:3c:4d:5e")
        self.assertEqual(formatar_mac(0x001A2B3C4D5E, "-", True), "00-1A-2B-3C-4D-5E")
        self.assertEqual(formatar_mac(0), "00:00:00:00:00:00")
        with self.assertRaises(ValueError):
            formatar_mac(1 << 48)

    def test_invalidos(self):
        for ruim in ["", "00:1a:2b:3c:4d", "00:1a:2b:3c:4d:5e:6f", "zz:1a:2b:3c:4d:5e",
                     "0:1a:2b:3c:4d:5e", "001a.2b3c", "00112233445"]:
            with self.assertRaises(ValueError, msg=ruim):
                parse_mac(ruim)

    def test_bits(self):
        self.assertTrue(eh_broadcast(parse_mac("ff:ff:ff:ff:ff:ff")))
        self.assertTrue(eh_multicast(parse_mac("01:00:5e:00:00:fb")))
        self.assertFalse(eh_multicast(parse_mac("00:1a:2b:3c:4d:5e")))
        self.assertTrue(eh_local(parse_mac("02:00:00:00:00:01")))
        self.assertFalse(eh_local(parse_mac("00:1a:2b:3c:4d:5e")))
        self.assertEqual(oui(parse_mac("00:1a:2b:3c:4d:5e")), 0x001A2B)

    def test_eui64(self):
        # exemplo clássico: 00:1A:2B:3C:4D:5E -> 021A:2BFF:FE3C:4D5E
        self.assertEqual(eui64(parse_mac("00:1a:2b:3c:4d:5e")), 0x021A2BFFFE3C4D5E)
        self.assertEqual(mac_de_eui64(0x021A2BFFFE3C4D5E), 0x001A2B3C4D5E)
        # bit U/L já ligado é invertido para 0
        self.assertEqual(eui64(parse_mac("02:00:00:00:00:01")) >> 56, 0x00)

    def test_eui64_invalido(self):
        with self.assertRaises(ValueError):
            mac_de_eui64(0x021A2B0000014D5E)

    def test_link_local(self):
        self.assertEqual(link_local_ipv6(parse_mac("00:1a:2b:3c:4d:5e")), "fe80::21a:2bff:fe3c:4d5e")


if __name__ == "__main__":
    unittest.main()
