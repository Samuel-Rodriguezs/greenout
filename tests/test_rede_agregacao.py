import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from rede_agregacao import agregar, normalizar, supernet_minimo
from rede_cidr import formatar_cidr, parse_cidr


def blocos(*textos):
    return [parse_cidr(t) for t in textos]


def txt(lista):
    return [formatar_cidr(*b) for b in lista]


class TestRedeAgregacao(unittest.TestCase):
    def test_quatro_c_viram_22(self):
        r = agregar(blocos("192.168.0.0/24", "192.168.1.0/24", "192.168.2.0/24", "192.168.3.0/24"))
        self.assertEqual(txt(r), ["192.168.0.0/22"])

    def test_nao_alinhados_nao_juntam(self):
        r = agregar(blocos("192.168.1.0/24", "192.168.2.0/24"))
        self.assertEqual(txt(r), ["192.168.1.0/24", "192.168.2.0/24"])

    def test_contidos_e_duplicados(self):
        r = agregar(blocos("10.0.0.0/8", "10.1.0.0/16", "10.0.0.0/8"))
        self.assertEqual(txt(r), ["10.0.0.0/8"])
        self.assertEqual(txt(normalizar(blocos("10.1.2.3/24"))), ["10.1.2.0/24"])

    def test_cascata(self):
        r = agregar(blocos("10.0.0.0/25", "10.0.0.128/25", "10.0.1.0/24"))
        self.assertEqual(txt(r), ["10.0.0.0/23"])

    def test_dois_slash_1_viram_slash_0(self):
        self.assertEqual(agregar([(0, 1), (0x80000000, 1)]), [(0, 0)])

    def test_vazio(self):
        self.assertEqual(agregar([]), [])

    def test_supernet_minimo(self):
        r = supernet_minimo(blocos("200.1.1.0/24", "200.1.3.0/24"))
        self.assertEqual(formatar_cidr(*r), "200.1.0.0/22")
        self.assertEqual(formatar_cidr(*supernet_minimo(blocos("1.2.3.4/32"))), "1.2.3.4/32")
        with self.assertRaises(ValueError):
            supernet_minimo([])


if __name__ == "__main__":
    unittest.main()
