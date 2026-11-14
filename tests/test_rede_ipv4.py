import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from rede_ipv4 import (classe_ipv4, eh_link_local, eh_loopback, eh_multicast,
                       eh_privado, formatar_ipv4, mascara_de_prefixo,
                       parse_ipv4, prefixo_de_mascara)


class TestRedeIPv4(unittest.TestCase):
    def test_parse_formatar(self):
        self.assertEqual(parse_ipv4("192.168.1.1"), 0xC0A80101)
        self.assertEqual(formatar_ipv4(0xC0A80101), "192.168.1.1")
        self.assertEqual(parse_ipv4("0.0.0.0"), 0)
        self.assertEqual(formatar_ipv4(0xFFFFFFFF), "255.255.255.255")

    def test_invalidos(self):
        for ruim in ["1.2.3", "1.2.3.256", "a.b.c.d", "01.2.3.4", "1.2.3.4.5", ""]:
            with self.assertRaises(ValueError, msg=ruim):
                parse_ipv4(ruim)
        with self.assertRaises(ValueError):
            formatar_ipv4(1 << 32)

    def test_classes(self):
        casos = {"10.0.0.1": "A", "127.255.0.0": "A", "128.0.0.0": "B",
                 "191.255.0.0": "B", "192.0.0.1": "C", "224.0.0.5": "D",
                 "240.0.0.0": "E"}
        for ip, c in casos.items():
            self.assertEqual(classe_ipv4(parse_ipv4(ip)), c)

    def test_mascaras(self):
        self.assertEqual(formatar_ipv4(mascara_de_prefixo(24)), "255.255.255.0")
        self.assertEqual(mascara_de_prefixo(0), 0)
        self.assertEqual(mascara_de_prefixo(32), 0xFFFFFFFF)
        self.assertEqual(prefixo_de_mascara(parse_ipv4("255.255.240.0")), 20)
        self.assertEqual(prefixo_de_mascara(0), 0)
        with self.assertRaises(ValueError):
            prefixo_de_mascara(parse_ipv4("255.0.255.0"))
        with self.assertRaises(ValueError):
            mascara_de_prefixo(33)

    def test_especiais(self):
        p = parse_ipv4
        self.assertTrue(eh_privado(p("172.31.255.255")))
        self.assertFalse(eh_privado(p("172.32.0.0")))
        self.assertTrue(eh_privado(p("192.168.10.1")))
        self.assertFalse(eh_privado(p("8.8.8.8")))
        self.assertTrue(eh_loopback(p("127.0.0.1")))
        self.assertFalse(eh_loopback(p("128.0.0.1")))
        self.assertTrue(eh_link_local(p("169.254.3.4")))
        self.assertTrue(eh_multicast(p("239.1.1.1")))
        self.assertFalse(eh_multicast(p("240.0.0.1")))


if __name__ == "__main__":
    unittest.main()
