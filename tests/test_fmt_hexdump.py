import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fmt_hexdump import ErroHexdump, hexdump, reverter


class TestFmtHexdump(unittest.TestCase):
    def test_formato_canonico(self):
        dump = hexdump(b"Hello, World!\n\x00\xff")
        esperado = ("00000000  48 65 6c 6c 6f 2c 20 57  6f 72 6c 64 21 0a 00 ff  |Hello, World!...|\n"
                    "00000010")
        self.assertEqual(dump, esperado)

    def test_ultima_linha_parcial(self):
        linhas = hexdump(b"abc").split("\n")
        self.assertEqual(linhas[0], "00000000  61 62 63                                          |abc|")
        self.assertEqual(linhas[1], "00000003")

    def test_vazio(self):
        self.assertEqual(hexdump(b""), "00000000")
        self.assertEqual(reverter("00000000"), b"")

    def test_linhas_repetidas(self):
        dados = b"A" * 16 * 5 + b"fim"
        dump = hexdump(dados)
        self.assertEqual(dump.split("\n")[1], "*")
        self.assertEqual(reverter(dump), dados)

    def test_ida_e_volta(self):
        for dados in (bytes(range(256)), b"\x00" * 100, b"abc", b"x" * 33):
            for larg in (16, 8, 7):
                with self.subTest(n=len(dados), larg=larg):
                    self.assertEqual(reverter(hexdump(dados, larg)), dados)

    def test_deslocamento(self):
        dump = hexdump(b"ab", deslocamento=0x100)
        self.assertTrue(dump.startswith("00000100  61 62"))
        self.assertEqual(reverter(dump), b"ab")

    def test_malformados(self):
        for ruim in ["lixo", "00000000  zz  |a|\n00000001", "00000000  61 62  |ab|\n00000009",
                     "00000000  61 62  |ab|\n00000005  63  |c|\n00000006", "*",
                     "00000000  61  |a|\n00000010"]:
            with self.subTest(ruim=ruim):
                with self.assertRaises(ErroHexdump):
                    reverter(ruim)
        with self.assertRaises(ErroHexdump):
            hexdump(b"a", 0)


if __name__ == "__main__":
    unittest.main()
