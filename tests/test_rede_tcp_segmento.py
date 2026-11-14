import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from rede_tcp_segmento import (Flags, SegmentoTCP, consumo_de_seq,
                               descrever_flags, parse, serializar)

A, B = 0xC0A80001, 0xC0A80002


class TestRedeTcpSegmento(unittest.TestCase):
    def test_syn_bytes(self):
        seg = serializar(SegmentoTCP(12345, 80, seq=1000, flags=Flags.SYN, mss=1460), A, B)
        self.assertEqual(len(seg), 24)
        self.assertEqual(seg[:16].hex(), "30390050000003e8000000006002ffff")
        self.assertEqual(seg[20:].hex(), "020405b4")

    def test_ida_e_volta(self):
        s = SegmentoTCP(80, 5000, seq=0xFFFFFFFF, ack=77, flags=Flags.ACK | Flags.PSH,
                        janela=1024, carga=b"GET / HTTP/1.1\r\n", urgente=0)
        self.assertEqual(parse(serializar(s, A, B), A, B), s)

    def test_mss_ida_e_volta(self):
        s = SegmentoTCP(1, 2, flags=Flags.SYN | Flags.ACK, mss=536)
        self.assertEqual(parse(serializar(s, A, B), A, B).mss, 536)

    def test_checksum_valida_pseudo_cabecalho(self):
        seg = serializar(SegmentoTCP(1, 2, carga=b"abc"), A, B)
        with self.assertRaises(ValueError):
            parse(seg, A, B + 1)
        ruim = bytearray(seg)
        ruim[-1] ^= 0xFF
        with self.assertRaises(ValueError):
            parse(bytes(ruim), A, B)

    def test_seq_modular(self):
        seg = serializar(SegmentoTCP(1, 2, seq=(1 << 32) + 5), A, B)
        self.assertEqual(struct.unpack("!I", seg[4:8])[0], 5)

    def test_flags(self):
        self.assertEqual(descrever_flags(Flags.SYN | Flags.ACK), "SYN|ACK")
        self.assertEqual(descrever_flags(Flags(0)), "-")
        self.assertEqual(int(Flags.FIN | Flags.ACK), 0x11)

    def test_consumo_seq(self):
        self.assertEqual(consumo_de_seq(SegmentoTCP(1, 2, flags=Flags.SYN)), 1)
        self.assertEqual(consumo_de_seq(SegmentoTCP(1, 2, flags=Flags.FIN | Flags.ACK, carga=b"xy")), 3)
        self.assertEqual(consumo_de_seq(SegmentoTCP(1, 2, flags=Flags.ACK)), 0)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            parse(b"\x00" * 19, A, B)
        seg = bytearray(serializar(SegmentoTCP(1, 2), A, B))
        seg[12] = 0x40  # data offset 4 < 5
        with self.assertRaises(ValueError):
            parse(bytes(seg), A, B)


if __name__ == "__main__":
    unittest.main()
