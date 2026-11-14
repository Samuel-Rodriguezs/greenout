import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from img_pnm import escrever_pnm, ler_pnm


class TestImgPnm(unittest.TestCase):
    def test_p2_com_comentario(self):
        dados = b"P2\n# comentario\n3 2\n255\n0 128 255\n10 20 30\n"
        formato, maxval, img = ler_pnm(dados)
        self.assertEqual((formato, maxval), ("P2", 255))
        self.assertEqual(img, [[0, 128, 255], [10, 20, 30]])

    def test_p3(self):
        _, _, img = ler_pnm(b"P3 2 1 255  255 0 0   0 0 255")
        self.assertEqual(img, [[(255, 0, 0), (0, 0, 255)]])

    def test_p5_binario(self):
        dados = b"P5\n2 2\n255\n" + bytes([0, 10, 200, 255])
        self.assertEqual(ler_pnm(dados)[2], [[0, 10], [200, 255]])

    def test_p5_bytes_de_espaco_nos_dados(self):
        dados = b"P5\n2 1\n255\n" + bytes([0x20, 0x0A])
        self.assertEqual(ler_pnm(dados)[2], [[32, 10]])

    def test_p6_binario(self):
        dados = b"P6\n1 2\n255\n" + bytes([1, 2, 3, 4, 5, 6])
        self.assertEqual(ler_pnm(dados)[2], [[(1, 2, 3)], [(4, 5, 6)]])

    def test_p5_16_bits(self):
        dados = b"P5\n2 1\n1023\n" + bytes([0x03, 0xFF, 0x01, 0x00])
        _, maxval, img = ler_pnm(dados)
        self.assertEqual(maxval, 1023)
        self.assertEqual(img, [[1023, 256]])

    def test_escrever_p5_bytes(self):
        saida = escrever_pnm([[0, 1], [2, 255]], "P5")
        self.assertEqual(saida, b"P5\n2 2\n255\n\x00\x01\x02\xff")

    def test_escrever_p2_texto(self):
        saida = escrever_pnm([[1, 2, 3], [4, 5, 6]], "P2")
        self.assertEqual(saida, b"P2\n3 2\n255\n1 2 3\n4 5 6\n")

    def test_ida_e_volta(self):
        gray = [[0, 50, 100], [150, 200, 255]]
        rgb = [[(1, 2, 3), (4, 5, 6)], [(250, 251, 252), (0, 0, 0)]]
        for fmt in ("P2", "P5"):
            self.assertEqual(ler_pnm(escrever_pnm(gray, fmt))[2], gray)
        for fmt in ("P3", "P6"):
            self.assertEqual(ler_pnm(escrever_pnm(rgb, fmt))[2], rgb)

    def test_erros(self):
        with self.assertRaises(ValueError):
            ler_pnm(b"P9\n1 1\n255\n0")
        with self.assertRaises(ValueError):
            ler_pnm(b"P5\n2 2\n255\n\x00")
        with self.assertRaises(ValueError):
            ler_pnm(b"P2\n2 1\n255\n1")
        with self.assertRaises(ValueError):
            escrever_pnm([[1]], "P6")
        with self.assertRaises(ValueError):
            escrever_pnm([[300]], "P5")


if __name__ == "__main__":
    unittest.main()
