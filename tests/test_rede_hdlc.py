import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from rede_hdlc import (FLAG, bits_para_bytes, bytes_para_bits, crc16_x25,
                       extrair_quadros, inserir_bits, montar_quadro,
                       remover_bits)


def b(texto):
    return [int(c) for c in texto]


class TestRedeHdlc(unittest.TestCase):
    def test_crc_vetor_padrao(self):
        self.assertEqual(crc16_x25(b"123456789"), 0x906E)

    def test_stuffing_basico(self):
        self.assertEqual(inserir_bits(b("0111110")), b("01111100"))
        self.assertEqual(inserir_bits(b("111111")), b("1111101"))
        self.assertEqual(inserir_bits(b("11111")), b("111110"))  # insere mesmo no fim
        self.assertEqual(inserir_bits(b("1111")), b("1111"))

    def test_stuffing_dez_uns(self):
        self.assertEqual(inserir_bits([1] * 10), b("11111011111" "0"))

    def test_stuffing_ida_e_volta(self):
        for dados in (b"\x7e", b"\xff\xff", b"\x7e\x7e\x00\xfe", bytes(range(256))):
            bits = bytes_para_bits(dados)
            enchido = inserir_bits(bits)
            self.assertNotIn([1] * 6, [enchido[i:i + 6] for i in range(len(enchido) - 5)])
            self.assertEqual(remover_bits(enchido), bits)

    def test_remover_seis_uns_erro(self):
        with self.assertRaises(ValueError):
            remover_bits(b("111111"))

    def test_bits_bytes(self):
        self.assertEqual(bytes_para_bits(b"\x01"), b("10000000"))  # LSB primeiro
        self.assertEqual(bits_para_bytes(bytes_para_bits(b"\xa5\x3c")), b"\xa5\x3c")
        with self.assertRaises(ValueError):
            bits_para_bytes([1, 0, 1])

    def test_quadro_ida_e_volta(self):
        q = montar_quadro(0x03, 0x13, b"ola\x7e mundo")
        self.assertEqual(q[:8], FLAG)
        self.assertEqual(q[-8:], FLAG)
        self.assertEqual(extrair_quadros(q), [(0x03, 0x13, b"ola\x7e mundo")])

    def test_dados_vazios(self):
        self.assertEqual(extrair_quadros(montar_quadro(1, 2, b"")), [(1, 2, b"")])

    def test_dois_quadros_com_flag_compartilhada(self):
        q1, q2 = montar_quadro(1, 0, b"um"), montar_quadro(2, 0, b"dois")
        fluxo = q1 + q2[8:]  # flag final de q1 serve de inicial de q2
        self.assertEqual(extrair_quadros(fluxo), [(1, 0, b"um"), (2, 0, b"dois")])

    def test_ruido_entre_quadros_e_corrupcao(self):
        q = montar_quadro(1, 0, b"dados")
        corrompido = list(q)
        corrompido[20] ^= 1
        self.assertEqual(extrair_quadros(corrompido), [])
        self.assertEqual(extrair_quadros(b("0101") + q + b("110")), [(1, 0, b"dados")])

    def test_flag_nao_aparece_no_miolo(self):
        q = montar_quadro(0x7E, 0x7E, b"\x7e\x7e\xff\xff")
        miolo = q[8:-8]
        self.assertNotIn(FLAG, [miolo[i:i + 8] for i in range(len(miolo) - 7)])
        self.assertEqual(extrair_quadros(q), [(0x7E, 0x7E, b"\x7e\x7e\xff\xff")])


if __name__ == "__main__":
    unittest.main()
