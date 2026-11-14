import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from rede_ipv4 import parse_ipv4 as ip
from rede_nat import NAT

PUB = ip("200.1.2.3")
H1 = (ip("192.168.0.10"), 5000)
H2 = (ip("192.168.0.11"), 5000)


class Relogio:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


class TestRedeNat(unittest.TestCase):
    def test_traducao_e_retorno(self):
        n = NAT(PUB, (1000, 2000))
        ext = n.traduzir_saida("tcp", H1)
        self.assertEqual(ext, (PUB, 1000))
        self.assertEqual(n.traduzir_entrada("tcp", 1000), H1)

    def test_mesma_origem_reusa_porta(self):
        n = NAT(PUB, (1000, 2000))
        self.assertEqual(n.traduzir_saida("tcp", H1), n.traduzir_saida("tcp", H1))
        self.assertEqual(len(n), 1)

    def test_hosts_com_mesma_porta_local_diferem(self):
        n = NAT(PUB, (1000, 2000))
        a, b = n.traduzir_saida("udp", H1), n.traduzir_saida("udp", H2)
        self.assertNotEqual(a[1], b[1])
        self.assertEqual(n.traduzir_entrada("udp", b[1]), H2)

    def test_protocolos_independentes(self):
        n = NAT(PUB, (1000, 2000))
        t = n.traduzir_saida("tcp", H1)
        u = n.traduzir_saida("udp", H1)
        self.assertEqual(t[1], 1000)
        self.assertEqual(u[1], 1001)
        self.assertIsNone(n.traduzir_entrada("icmp", 1000))

    def test_entrada_sem_traducao_descartada(self):
        self.assertIsNone(NAT(PUB).traduzir_entrada("tcp", 55555))

    def test_timeout(self):
        r = Relogio()
        n = NAT(PUB, (1000, 2000), timeout=30, relogio=r)
        porta = n.traduzir_saida("tcp", H1)[1]
        r.t = 29
        self.assertEqual(n.traduzir_entrada("tcp", porta), H1)  # renova
        r.t = 58
        self.assertEqual(n.traduzir_entrada("tcp", porta), H1)
        r.t = 88
        self.assertIsNone(n.traduzir_entrada("tcp", porta))
        self.assertEqual(len(n), 0)

    def test_expirar_libera_porta(self):
        r = Relogio()
        n = NAT(PUB, (1000, 1000), timeout=10, relogio=r)  # uma única porta
        n.traduzir_saida("tcp", H1)
        with self.assertRaises(RuntimeError):  # relógio parado: porta ainda ocupada
            n.traduzir_saida("tcp", H2)
        r.t = 10
        self.assertEqual(n.traduzir_saida("tcp", H2), (PUB, 1000))

    def test_redirecionamento_estatico(self):
        r = Relogio()
        n = NAT(PUB, timeout=1, relogio=r)
        n.adicionar_redirecionamento("tcp", 80, H1)
        r.t = 10_000
        self.assertEqual(n.traduzir_entrada("tcp", 80), H1)
        with self.assertRaises(ValueError):
            n.adicionar_redirecionamento("tcp", 80, H2)

    def test_faixa_invalida(self):
        with self.assertRaises(ValueError):
            NAT(PUB, (0, 10))
        with self.assertRaises(ValueError):
            NAT(PUB, (20, 10))


if __name__ == "__main__":
    unittest.main()
