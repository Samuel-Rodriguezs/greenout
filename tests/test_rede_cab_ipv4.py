import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from rede_cab_ipv4 import (FLAG_DF, FLAG_MF, PROTO_UDP, CabecalhoIPv4,
                           decrementar_ttl, fragmentar, parse, remontar,
                           serializar)
from rede_ipv4 import parse_ipv4

SRC, DST = parse_ipv4("192.168.0.1"), parse_ipv4("192.168.0.199")


class TestRedeCabIPv4(unittest.TestCase):
    def test_vetor_conhecido(self):
        c = CabecalhoIPv4(SRC, DST, PROTO_UDP, comprimento_total=0x73, flags=FLAG_DF, ttl=64)
        self.assertEqual(serializar(c).hex(), "45000073000040004011b861c0a80001c0a800c7")

    def test_ida_e_volta(self):
        c = CabecalhoIPv4(SRC, DST, 6, 100, 33, 0xBEEF, FLAG_MF, 185, tos=0x10)
        self.assertEqual(parse(serializar(c)), c)

    def test_opcoes(self):
        c = CabecalhoIPv4(SRC, DST, 1, 24, opcoes=b"\x01\x01\x01\x00")
        dados = serializar(c)
        self.assertEqual(dados[0], 0x46)
        self.assertEqual(parse(dados).opcoes, c.opcoes)
        with self.assertRaises(ValueError):
            serializar(CabecalhoIPv4(SRC, DST, 1, opcoes=b"\x01"))

    def test_parse_invalidos(self):
        bom = bytearray(serializar(CabecalhoIPv4(SRC, DST, 6)))
        with self.assertRaises(ValueError):
            parse(bytes(bom[:19]))
        ruim = bytearray(bom)
        ruim[8] ^= 0xFF
        with self.assertRaises(ValueError):
            parse(bytes(ruim))
        v6 = bytearray(bom)
        v6[0] = 0x65
        with self.assertRaises(ValueError):
            parse(bytes(v6))

    def test_ttl(self):
        c = CabecalhoIPv4(SRC, DST, 6, ttl=2)
        c2 = decrementar_ttl(c)
        self.assertEqual(c2.ttl, 1)
        with self.assertRaises(TimeoutError):
            decrementar_ttl(c2)

    def test_fragmentacao_classica(self):
        # 4000 bytes de dados, MTU 1500: 1480 + 1480 + 1040
        c = CabecalhoIPv4(SRC, DST, 17, 4020, identificacao=7)
        carga = bytes(i % 251 for i in range(4000))
        frags = fragmentar(c, carga, 1500)
        self.assertEqual([len(p) for _, p in frags], [1480, 1480, 1040])
        self.assertEqual([h.deslocamento for h, _ in frags], [0, 185, 370])
        self.assertEqual([h.mais_fragmentos for h, _ in frags], [True, True, False])
        self.assertEqual([h.comprimento_total for h, _ in frags], [1500, 1500, 1060])
        self.assertEqual(remontar(list(reversed(frags))), carga)

    def test_sem_fragmentar(self):
        c = CabecalhoIPv4(SRC, DST, 17)
        r = fragmentar(c, b"abc", 1500)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0][0].comprimento_total, 23)

    def test_df_excede(self):
        c = CabecalhoIPv4(SRC, DST, 17, flags=FLAG_DF)
        with self.assertRaises(ValueError):
            fragmentar(c, bytes(2000), 1500)

    def test_fragmento_de_fragmento_mantem_mf(self):
        c = CabecalhoIPv4(SRC, DST, 17, flags=FLAG_MF, deslocamento=100)
        frags = fragmentar(c, bytes(200), 148)  # 128 por fragmento
        self.assertTrue(all(h.mais_fragmentos for h, _ in frags))
        self.assertEqual(frags[1][0].deslocamento, 116)

    def test_remontar_com_buraco(self):
        c = CabecalhoIPv4(SRC, DST, 17)
        frags = fragmentar(c, bytes(4000), 1500)
        with self.assertRaises(ValueError):
            remontar([frags[0], frags[2]])
        with self.assertRaises(ValueError):
            remontar(frags[:2])
        with self.assertRaises(ValueError):
            remontar(frags[1:])


if __name__ == "__main__":
    unittest.main()
