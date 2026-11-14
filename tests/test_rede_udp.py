import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from rede_udp import DatagramaUDP, parse, pseudo_cabecalho, serializar

A, B = 0x0A000001, 0x0A000002  # 10.0.0.1 -> 10.0.0.2


class TestRedeUdp(unittest.TestCase):
    def test_pseudo_cabecalho(self):
        self.assertEqual(pseudo_cabecalho(A, B, 17, 10).hex(), "0a0000010a0000020011000a")

    def test_checksum_calculado_a_mao(self):
        # pseudo: 0a00 0001 0a00 0002 0011 000a ; udp: 03e8 07d0 000a 0000 ; dados "hi"=6869
        palavras = [0x0A00, 0x0001, 0x0A00, 0x0002, 0x0011, 0x000A,
                    0x03E8, 0x07D0, 0x000A, 0x0000, 0x6869]
        total = sum(palavras)
        while total >> 16:
            total = (total & 0xFFFF) + (total >> 16)
        esperado = ~total & 0xFFFF
        seg = serializar(DatagramaUDP(1000, 2000, b"hi"), A, B)
        self.assertEqual(struct.unpack("!H", seg[6:8])[0], esperado)
        self.assertEqual(seg[:6].hex(), "03e807d0000a")

    def test_ida_e_volta(self):
        d = DatagramaUDP(53, 40000, b"consulta dns")
        r = parse(serializar(d, A, B), A, B)
        self.assertEqual((r.porta_origem, r.porta_destino, r.carga), (53, 40000, b"consulta dns"))
        self.assertEqual(r.comprimento, 8 + 12)

    def test_carga_impar_e_vazia(self):
        for carga in (b"", b"x", b"abc"):
            seg = serializar(DatagramaUDP(1, 2, carga), A, B)
            self.assertEqual(parse(seg, A, B).carga, carga)

    def test_corrupcao_e_endereco_errado(self):
        seg = bytearray(serializar(DatagramaUDP(1, 2, b"dados"), A, B))
        seg[-1] ^= 0x01
        with self.assertRaises(ValueError):
            parse(bytes(seg), A, B)
        ok = serializar(DatagramaUDP(1, 2, b"dados"), A, B)
        with self.assertRaises(ValueError):
            parse(ok, A, 0x0A000003)  # pseudo-cabeçalho diferente

    def test_checksum_zero_vira_ffff(self):
        # procura uma carga cujo checksum natural seja 0 e verifica a substituição
        for n in range(65536):
            carga = struct.pack("!H", n)
            seg = serializar(DatagramaUDP(0, 0, carga), 0, 0)
            soma = struct.unpack("!H", seg[6:8])[0]
            self.assertNotEqual(soma, 0)
            if soma == 0xFFFF:
                self.assertEqual(parse(seg, 0, 0).carga, carga)
                break
        else:
            self.fail("nenhum caso com checksum 0xFFFF encontrado")

    def test_sem_checksum_aceito(self):
        seg = struct.pack("!HHHH", 1, 2, 9, 0) + b"z"
        self.assertEqual(parse(seg, A, B).carga, b"z")

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            parse(b"\x00" * 7, A, B)
        with self.assertRaises(ValueError):
            parse(struct.pack("!HHHH", 1, 2, 20, 0), A, B)


if __name__ == "__main__":
    unittest.main()
