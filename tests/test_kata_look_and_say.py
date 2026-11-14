import sys
import unittest
from itertools import islice
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_look_and_say import decodificar, proximo, sequencia, termo


class TestKataLookAndSay(unittest.TestCase):
    def test_primeiros_termos(self):
        esperado = ["1", "11", "21", "1211", "111221", "312211", "13112221"]
        self.assertEqual(list(islice(sequencia(), 7)), esperado)

    def test_proximo(self):
        self.assertEqual(proximo("1"), "11")
        self.assertEqual(proximo("1211"), "111221")
        self.assertEqual(proximo("3333"), "43")
        self.assertEqual(proximo("1" * 12), "121")

    def test_termo(self):
        self.assertEqual(termo(1), "1")
        self.assertEqual(termo(8), "1113213211")

    def test_outra_semente(self):
        self.assertEqual(proximo("22"), "22")
        self.assertEqual(termo(5, "22"), "22")

    def test_comprimento_cresce(self):
        tamanhos = [len(termo(n)) for n in range(1, 12)]
        self.assertEqual(tamanhos, [1, 2, 2, 4, 6, 6, 8, 10, 14, 20, 26])

    def test_nunca_tem_digito_maior_que_3(self):
        self.assertTrue(set(termo(25)) <= set("123"))

    def test_decodificar(self):
        self.assertEqual(decodificar("111221"), "1211")
        for n in range(2, 10):
            self.assertEqual(decodificar(termo(n)), termo(n - 1))

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            proximo("")
        with self.assertRaises(ValueError):
            proximo("1a")
        with self.assertRaises(ValueError):
            termo(0)
        with self.assertRaises(ValueError):
            decodificar("121")


if __name__ == "__main__":
    unittest.main()
