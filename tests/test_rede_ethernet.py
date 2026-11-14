import sys
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from rede_ethernet import Quadro, crc32, parse, serializar

DST, SRC = 0xFFFFFFFFFFFF, 0x001A2B3C4D5E


class TestRedeEthernet(unittest.TestCase):
    def test_crc32_vetor_padrao(self):
        self.assertEqual(crc32(b"123456789"), 0xCBF43926)
        self.assertEqual(crc32(b""), 0)

    def test_crc32_igual_zlib(self):
        for dados in (b"a", b"ethernet", bytes(range(256)) * 3):
            self.assertEqual(crc32(dados), zlib.crc32(dados))

    def test_padding_ate_64(self):
        f = serializar(Quadro(DST, SRC, 0x0806, b"abc"))
        self.assertEqual(len(f), 64)  # 14 + 46 + 4
        self.assertEqual(f[:14].hex(), "ffffffffffff001a2b3c4d5e0806")

    def test_sem_padding_carga_maior(self):
        f = serializar(Quadro(DST, SRC, 0x0800, bytes(100)))
        self.assertEqual(len(f), 14 + 100 + 4)
        self.assertEqual(serializar(Quadro(DST, SRC, 0x0800, bytes(1500))).__len__(), 1518)

    def test_ida_e_volta(self):
        carga = bytes(range(60))
        q = Quadro(SRC, DST, 0x0800, carga)
        self.assertEqual(parse(serializar(q)), q)

    def test_fcs_little_endian(self):
        f = serializar(Quadro(DST, SRC, 0x0800, bytes(50)))
        self.assertEqual(int.from_bytes(f[-4:], "little"), zlib.crc32(f[:-4]))

    def test_vlan(self):
        q = Quadro(DST, SRC, 0x0800, bytes(50), vlan=100)
        f = serializar(q)
        self.assertEqual(f[12:16].hex(), "81000064")
        self.assertEqual(parse(f), q)

    def test_corrupcao(self):
        f = bytearray(serializar(Quadro(DST, SRC, 0x0800, bytes(50))))
        f[20] ^= 0x04
        with self.assertRaises(ValueError):
            parse(bytes(f))

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            serializar(Quadro(DST, SRC, 0x0800, bytes(1501)))
        with self.assertRaises(ValueError):
            serializar(Quadro(DST, SRC, 0x0800, b"", vlan=4096))
        with self.assertRaises(ValueError):
            parse(bytes(63))


if __name__ == "__main__":
    unittest.main()
