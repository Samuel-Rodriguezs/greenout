import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from rede_arp import (MAC_ZERO, OP_REQUISICAO, OP_RESPOSTA, CacheARP, HostARP,
                      PacoteARP, SegmentoLAN, parse, serializar)
from rede_ipv4 import parse_ipv4 as ip
from rede_mac import parse_mac as mac


class Relogio:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


class TestRedeArp(unittest.TestCase):
    def test_pacote_vetor(self):
        p = PacoteARP(OP_REQUISICAO, mac("00:11:22:33:44:55"), ip("192.168.1.10"),
                      MAC_ZERO, ip("192.168.1.1"))
        self.assertEqual(serializar(p).hex(),
                         "0001" "0800" "06" "04" "0001" "001122334455" "c0a8010a"
                         "000000000000" "c0a80101")
        self.assertEqual(parse(serializar(p)), p)

    def test_parse_invalido(self):
        base = serializar(PacoteARP(OP_RESPOSTA, 1, 2, 3, 4))
        with self.assertRaises(ValueError):
            parse(base[:27])
        with self.assertRaises(ValueError):
            parse(b"\x00\x02" + base[2:])  # hardware desconhecido
        with self.assertRaises(ValueError):
            parse(base[:6] + b"\x00\x09" + base[8:])

    def test_cache_ttl(self):
        r = Relogio()
        c = CacheARP(ttl=10, relogio=r)
        c.inserir(1, 0xAA)
        r.t = 9.9
        self.assertEqual(c.consultar(1), 0xAA)
        r.t = 10
        self.assertIsNone(c.consultar(1))
        self.assertEqual(len(c), 0)

    def test_cache_renova_e_limpa(self):
        r = Relogio()
        c = CacheARP(ttl=10, relogio=r)
        c.inserir(1, 0xA)
        c.inserir(2, 0xB)
        r.t = 8
        c.inserir(1, 0xA)  # renova
        r.t = 12
        self.assertEqual(c.limpar_expirados(), 1)
        self.assertEqual(c.consultar(1), 0xA)
        self.assertTrue(c.remover(1))
        self.assertFalse(c.remover(1))
        with self.assertRaises(ValueError):
            CacheARP(ttl=0)

    def test_resolucao_na_lan(self):
        lan = SegmentoLAN()
        a = HostARP(ip("10.0.0.1"), mac("aa:aa:aa:aa:aa:01"))
        b = HostARP(ip("10.0.0.2"), mac("aa:aa:aa:aa:aa:02"))
        c = HostARP(ip("10.0.0.3"), mac("aa:aa:aa:aa:aa:03"))
        for h in (a, b, c):
            lan.anexar(h)
        self.assertEqual(a.resolver(ip("10.0.0.2")), mac("aa:aa:aa:aa:aa:02"))
        self.assertEqual(lan.pacotes_enviados, 2)  # request + reply
        # o alvo aprendeu o solicitante; terceiros não
        self.assertEqual(b.cache.consultar(ip("10.0.0.1")), a.mac)
        self.assertIsNone(c.cache.consultar(ip("10.0.0.1")))
        # segunda consulta vem do cache, sem tráfego
        a.resolver(ip("10.0.0.2"))
        self.assertEqual(lan.pacotes_enviados, 2)

    def test_sem_resposta_e_proprio_ip(self):
        lan = SegmentoLAN()
        a = HostARP(ip("10.0.0.1"), 0x01)
        lan.anexar(a)
        self.assertIsNone(a.resolver(ip("10.0.0.99")))
        self.assertEqual(a.resolver(ip("10.0.0.1")), 0x01)
        isolado = HostARP(5, 6)
        self.assertIsNone(isolado.resolver(7))

    def test_expiracao_provoca_novo_request(self):
        r = Relogio()
        lan = SegmentoLAN()
        a = HostARP(1, 0xA, CacheARP(5, r))
        b = HostARP(2, 0xB, CacheARP(5, r))
        lan.anexar(a)
        lan.anexar(b)
        a.resolver(2)
        r.t = 6
        a.resolver(2)
        self.assertEqual(lan.pacotes_enviados, 4)


if __name__ == "__main__":
    unittest.main()
