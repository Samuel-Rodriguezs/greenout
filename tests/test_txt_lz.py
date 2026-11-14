import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from txt_lz import lz77_comprimir, lz77_descomprimir, lzw_comprimir, lzw_descomprimir

AMOSTRAS = ["", "a", "aaaaaaaaaa", "abracadabra abracadabra", "ação não éção", "abcabcabcabcx", "TOBEORNOTTOBEORTOBEORNOT"]


class TestLZ(unittest.TestCase):
    def test_lz77_ida_e_volta(self):
        for s in AMOSTRAS:
            self.assertEqual(lz77_descomprimir(lz77_comprimir(s)), s, s)

    def test_lz77_comprime_repeticao(self):
        self.assertEqual(len(lz77_comprimir("aaaaaaaaaa")), 2)
        self.assertEqual(lz77_comprimir("aaaaaaaaaa")[1], (1, 8, "a"))

    def test_lz77_janela_pequena(self):
        s = "abcdefabcdef" * 3
        self.assertEqual(lz77_descomprimir(lz77_comprimir(s, janela=3, lookahead=4)), s)

    def test_lz77_erros(self):
        with self.assertRaises(ValueError):
            lz77_comprimir("a", janela=0)
        with self.assertRaises(ValueError):
            lz77_descomprimir([(5, 2, "a")])

    def test_lzw_ida_e_volta(self):
        for s in AMOSTRAS:
            self.assertEqual(lzw_descomprimir(lzw_comprimir(s)), s, s)

    def test_lzw_conhecido(self):
        self.assertEqual(
            lzw_comprimir("TOBEORNOTTOBEORTOBEORNOT"),
            [84, 79, 66, 69, 79, 82, 78, 79, 84, 256, 258, 260, 265, 259, 261, 263],
        )

    def test_lzw_caso_kwkwk(self):
        self.assertEqual(lzw_descomprimir(lzw_comprimir("aaaaaaa")), "aaaaaaa")

    def test_lzw_erros(self):
        with self.assertRaises(ValueError):
            lzw_descomprimir([65, 999])
        with self.assertRaises(ValueError):
            lzw_descomprimir([300])


if __name__ == "__main__":
    unittest.main()
