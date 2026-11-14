import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from rede_cidr import (broadcast, dividir, endereco_rede, formatar_cidr, hosts,
                       parse_cidr, prefixo_para_hosts, total_hosts, vlsm)
from rede_ipv4 import formatar_ipv4


class TestRedeCidr(unittest.TestCase):
    def test_rede_broadcast(self):
        ip, p = parse_cidr("192.168.10.77/26")
        self.assertEqual(formatar_ipv4(endereco_rede(ip, p)), "192.168.10.64")
        self.assertEqual(formatar_ipv4(broadcast(ip, p)), "192.168.10.127")

    def test_total_hosts(self):
        self.assertEqual(total_hosts(24), 254)
        self.assertEqual(total_hosts(30), 2)
        self.assertEqual(total_hosts(31), 2)
        self.assertEqual(total_hosts(32), 1)
        self.assertEqual(total_hosts(0), (1 << 32) - 2)

    def test_hosts(self):
        ip, p = parse_cidr("10.0.0.0/30")
        self.assertEqual([formatar_ipv4(h) for h in hosts(ip, p)], ["10.0.0.1", "10.0.0.2"])
        ip, p = parse_cidr("10.0.0.4/31")
        self.assertEqual(len(list(hosts(ip, p))), 2)
        ip, p = parse_cidr("10.0.0.9/32")
        self.assertEqual(list(hosts(ip, p)), [ip])

    def test_dividir(self):
        ip, p = parse_cidr("172.16.0.0/24")
        subs = dividir(ip, p, 26)
        self.assertEqual([formatar_cidr(*s) for s in subs],
                         ["172.16.0.0/26", "172.16.0.64/26", "172.16.0.128/26", "172.16.0.192/26"])
        self.assertEqual(dividir(ip, p, 24), [(endereco_rede(ip, p), 24)])
        with self.assertRaises(ValueError):
            dividir(ip, p, 23)

    def test_prefixo_para_hosts(self):
        self.assertEqual(prefixo_para_hosts(100), 25)
        self.assertEqual(prefixo_para_hosts(2), 30)
        self.assertEqual(prefixo_para_hosts(1), 30)
        self.assertEqual(prefixo_para_hosts(254), 24)
        self.assertEqual(prefixo_para_hosts(255), 23)
        with self.assertRaises(ValueError):
            prefixo_para_hosts(0)

    def test_vlsm(self):
        ip, p = parse_cidr("192.168.1.0/24")
        r = vlsm(ip, p, {"A": 60, "B": 28, "C": 10, "D": 2})
        self.assertEqual(formatar_cidr(*r["A"]), "192.168.1.0/26")
        self.assertEqual(formatar_cidr(*r["B"]), "192.168.1.64/27")
        self.assertEqual(formatar_cidr(*r["C"]), "192.168.1.96/28")
        self.assertEqual(formatar_cidr(*r["D"]), "192.168.1.112/30")

    def test_vlsm_estouro(self):
        ip, p = parse_cidr("192.168.1.0/25")
        with self.assertRaises(ValueError):
            vlsm(ip, p, {"A": 100, "B": 100})

    def test_cidr_invalido(self):
        for ruim in ["1.2.3.4", "1.2.3.4/33", "1.2.3.4/x"]:
            with self.assertRaises(ValueError):
                parse_cidr(ruim)


if __name__ == "__main__":
    unittest.main()
