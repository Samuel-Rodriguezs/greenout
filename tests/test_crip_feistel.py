import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from crip_feistel import cbc_cifrar, cbc_decifrar, cifrar_bloco, ctr, decifrar_bloco, pad, unpad

CH = b"chave-secreta"


class TestFeistel(unittest.TestCase):
    def test_bloco_reversivel(self):
        b = b"12345678"
        c = cifrar_bloco(b, CH)
        self.assertNotEqual(c, b)
        self.assertEqual(decifrar_bloco(c, CH), b)
        self.assertNotEqual(cifrar_bloco(b, b"outra"), c)

    def test_bloco_tamanho(self):
        with self.assertRaises(ValueError):
            cifrar_bloco(b"curto", CH)

    def test_pad(self):
        self.assertEqual(pad(b""), b"\x08" * 8)
        self.assertEqual(len(pad(b"12345678")), 16)
        self.assertEqual(unpad(pad(b"abc")), b"abc")
        with self.assertRaises(ValueError):
            unpad(b"abcdefg\x09")

    def test_cbc(self):
        for n in (0, 1, 7, 8, 9, 100):
            m = bytes(range(n))
            self.assertEqual(cbc_decifrar(cbc_cifrar(m, CH), CH), m)

    def test_cbc_iv_fixo_e_encadeamento(self):
        iv = b"\x00" * 8
        c = cbc_cifrar(b"A" * 16, CH, iv)
        self.assertNotEqual(c[8:16], c[16:24])  # blocos iguais, cifrados diferentes
        self.assertEqual(cbc_cifrar(b"A" * 16, CH, iv), c)

    def test_cbc_adulterado(self):
        c = bytearray(cbc_cifrar(b"mensagem", CH))
        with self.assertRaises(ValueError):
            cbc_decifrar(bytes(c[:-3]), CH)

    def test_ctr(self):
        m = "texto longo em português com acentuação".encode()
        c = ctr(m, CH, b"nnnn")
        self.assertEqual(len(c), len(m))
        self.assertEqual(ctr(c, CH, b"nnnn"), m)
        self.assertNotEqual(ctr(m, CH, b"mmmm"), c)
        self.assertEqual(ctr(b"", CH, b"nnnn"), b"")
        with self.assertRaises(ValueError):
            ctr(m, CH, b"n")


if __name__ == "__main__":
    unittest.main()
