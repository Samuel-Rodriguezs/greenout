import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from rede_checksum import (atualizar_incremental, checksum, soma_complemento_um,
                           verificar)


class TestRedeChecksum(unittest.TestCase):
    def test_exemplo_rfc1071(self):
        dados = bytes.fromhex("0001f203f4f5f6f7")
        self.assertEqual(soma_complemento_um(dados), 0xDDF2)
        self.assertEqual(checksum(dados), 0x220D)

    def test_cabecalho_ipv4_conhecido(self):
        cab = bytes.fromhex("450000730000400040110000c0a80001c0a800c7")
        self.assertEqual(checksum(cab), 0xB861)
        completo = cab[:10] + bytes.fromhex("b861") + cab[12:]
        self.assertTrue(verificar(completo))

    def test_tamanho_impar(self):
        self.assertEqual(checksum(b"\x01"), 0xFEFF)
        self.assertEqual(checksum(b"\x01"), checksum(b"\x01\x00"))

    def test_vazio_e_zeros(self):
        self.assertEqual(checksum(b""), 0xFFFF)
        self.assertEqual(checksum(b"\x00" * 10), 0xFFFF)

    def test_corrupcao_detectada(self):
        cab = bytes.fromhex("450000730000400040110000c0a80001c0a800c7")
        completo = bytearray(cab[:10] + bytes.fromhex("b861") + cab[12:])
        completo[3] ^= 0x01
        self.assertFalse(verificar(bytes(completo)))

    def test_carry_circular(self):
        self.assertEqual(soma_complemento_um(b"\xff\xff\x00\x01"), 0x0001)

    def test_incremental(self):
        cab = bytearray.fromhex("450000730000400040110000c0a80001c0a800c7")
        antigo = checksum(bytes(cab))
        # troca o TTL/protocolo (palavra em offset 8): 0x4011 -> 0x3f11
        cab[8] = 0x3F
        novo_completo = checksum(bytes(cab))
        self.assertEqual(atualizar_incremental(antigo, 0x4011, 0x3F11), novo_completo)


if __name__ == "__main__":
    unittest.main()
