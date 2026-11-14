import sys
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import sig_crc as c

CHECK = b"123456789"


class TestCRC(unittest.TestCase):
    def test_valores_de_verificacao_padrao(self):
        self.assertEqual(c.crc8(CHECK), 0xF4)
        self.assertEqual(c.crc16_ccitt(CHECK), 0x29B1)
        self.assertEqual(c.crc32(CHECK), 0xCBF43926)

    def test_crc32_igual_zlib(self):
        for dados in (b"", b"a", b"sinais e sistemas", bytes(range(256))):
            self.assertEqual(c.crc32(dados), zlib.crc32(dados))

    def test_vazio(self):
        self.assertEqual(c.crc8(b""), 0)
        self.assertEqual(c.crc16_ccitt(b""), 0xFFFF)

    def test_anexar_e_verificar(self):
        q = c.anexar_crc16(b"hello")
        self.assertEqual(len(q), 7)
        self.assertTrue(c.verificar_crc16(q))

    def test_detecta_erro_de_um_bit(self):
        q = bytearray(c.anexar_crc16(b"mensagem importante"))
        for i in range(len(q)):
            for bit in range(8):
                q[i] ^= 1 << bit
                self.assertFalse(c.verificar_crc16(bytes(q)))
                q[i] ^= 1 << bit

    def test_quadro_curto(self):
        self.assertFalse(c.verificar_crc16(b"a"))

    def test_propriedade_do_resto_zero(self):
        # CRC sobre dados + CRC (big-endian) é zero para CRC-16 sem xor final
        q = c.anexar_crc16(CHECK)
        self.assertEqual(c.crc16_ccitt(q), 0)

    def test_blocos(self):
        self.assertEqual(c.dividir_em_blocos(b"abcde", 2), [b"ab", b"cd", b"e"])
        a = c.crcs_por_bloco(b"aaaabbbbcccc", 4)
        b = c.crcs_por_bloco(b"aaaabXbbcccc", 4)
        self.assertEqual([x != y for x, y in zip(a, b)], [False, True, False])
        with self.assertRaises(ValueError):
            c.dividir_em_blocos(b"x", 0)


if __name__ == "__main__":
    unittest.main()
