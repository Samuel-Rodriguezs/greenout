import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from rede_ipv4 import parse_ipv4 as ip
from rede_roteamento import TabelaRoteamento


def montar():
    t = TabelaRoteamento()
    t.adicionar("0.0.0.0/0", "10.0.0.254", "eth0")
    t.adicionar("10.0.0.0/8", "10.1.1.1", "eth1")
    t.adicionar("10.1.0.0/16", "10.1.1.2", "eth2")
    t.adicionar("10.1.2.0/24", None, "eth3")
    return t


class TestRedeRoteamento(unittest.TestCase):
    def test_longest_prefix_match(self):
        t = montar()
        casos = {
            "10.1.2.77": "eth3",
            "10.1.3.1": "eth2",
            "10.200.0.1": "eth1",
            "8.8.8.8": "eth0",
        }
        for destino, iface in casos.items():
            self.assertEqual(t.buscar(ip(destino)).interface, iface, destino)

    def test_sem_rota_padrao(self):
        t = TabelaRoteamento()
        t.adicionar("192.168.0.0/16", None, "lan")
        self.assertIsNone(t.buscar(ip("1.1.1.1")))
        self.assertEqual(t.buscar(ip("192.168.255.255")).interface, "lan")
        self.assertIsNone(t.buscar(ip("192.169.0.0")))

    def test_host_route(self):
        t = montar()
        t.adicionar("10.1.2.5/32", "10.9.9.9", "tun0")
        self.assertEqual(t.buscar(ip("10.1.2.5")).interface, "tun0")
        self.assertEqual(t.buscar(ip("10.1.2.6")).interface, "eth3")

    def test_remocao_cai_para_menos_especifica(self):
        t = montar()
        self.assertTrue(t.remover("10.1.2.0/24"))
        self.assertFalse(t.remover("10.1.2.0/24"))
        self.assertFalse(t.remover("172.16.0.0/12"))
        self.assertEqual(t.buscar(ip("10.1.2.77")).interface, "eth2")
        self.assertEqual(len(t), 3)

    def test_metrica_em_empate(self):
        t = TabelaRoteamento()
        t.adicionar("10.0.0.0/8", "a", "e0", 10)
        t.adicionar("10.0.0.0/8", "b", "e1", 20)  # pior: ignorada
        self.assertEqual(t.buscar(ip("10.1.1.1")).proximo_salto, "a")
        t.adicionar("10.0.0.0/8", "c", "e2", 5)  # melhor: substitui
        self.assertEqual(t.buscar(ip("10.1.1.1")).proximo_salto, "c")
        self.assertEqual(len(t), 1)

    def test_bits_de_host_ignorados(self):
        t = TabelaRoteamento()
        r = t.adicionar("10.1.2.3/24", None, "x")
        self.assertEqual(r.rede, ip("10.1.2.0"))

    def test_listagem(self):
        t = montar()
        self.assertEqual([str(r).split()[0] for r in t.rotas()],
                         ["0.0.0.0/0", "10.0.0.0/8", "10.1.0.0/16", "10.1.2.0/24"])
        self.assertIn("direta", str(list(t.rotas())[-1]))
        self.assertIn("via 10.0.0.254", str(next(iter(t.rotas()))))

    def test_cidr_invalido(self):
        with self.assertRaises(ValueError):
            TabelaRoteamento().adicionar("10.0.0.0/40", None, "x")


if __name__ == "__main__":
    unittest.main()
