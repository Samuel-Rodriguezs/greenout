import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from crip_xor_otp import (
    gerar_chave, otp_cifrar, otp_decifrar, quebrar_xor_um_byte, recuperar_xor_de_mensagens, xor_bytes, xor_repetido,
)


class TestXorOtp(unittest.TestCase):
    def test_xor_basico(self):
        self.assertEqual(xor_bytes(b"\x0f\xf0", b"\xff\xff"), b"\xf0\x0f")
        with self.assertRaises(ValueError):
            xor_bytes(b"a", b"ab")

    def test_repetido_involutivo(self):
        m = b"mensagem secreta"
        self.assertEqual(xor_repetido(xor_repetido(m, b"abc"), b"abc"), m)
        with self.assertRaises(ValueError):
            xor_repetido(m, b"")

    def test_otp(self):
        m = "ação".encode()
        k = gerar_chave(len(m))
        self.assertEqual(otp_decifrar(otp_cifrar(m, k), k), m)
        self.assertEqual(otp_cifrar(b"", b""), b"")
        with self.assertRaises(ValueError):
            otp_cifrar(b"abcd", b"ab")

    def test_reuso_vaza_xor(self):
        k = gerar_chave(5)
        c1, c2 = otp_cifrar(b"ola!!", k), otp_cifrar(b"tchau", k)
        self.assertEqual(recuperar_xor_de_mensagens(c1, c2), xor_bytes(b"ola!!", b"tchau"))

    def test_quebra_um_byte(self):
        original = b"The quick brown fox jumps over the lazy dog and runs into the forest"
        k, txt = quebrar_xor_um_byte(bytes(b ^ 0x5A for b in original))
        self.assertEqual((k, txt), (0x5A, original))


if __name__ == "__main__":
    unittest.main()
