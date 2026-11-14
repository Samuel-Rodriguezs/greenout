import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from proj_huffman import construir_codigos, codificar, decodificar


class TestHuffman(unittest.TestCase):
    def test_ida_e_volta(self):
        texto = "abracadabra alakazam"
        cod = construir_codigos(texto)
        self.assertEqual(decodificar(codificar(texto, cod), cod), texto)

    def test_prefixo_livre(self):
        cod = construir_codigos("aaaabbbccd")
        for a in cod.values():
            for b in cod.values():
                if a != b:
                    self.assertFalse(b.startswith(a))

    def test_mais_frequente_codigo_menor(self):
        cod = construir_codigos("aaaaaaaabbbccd")
        self.assertLessEqual(len(cod["a"]), len(cod["d"]))

    def test_menos_bits_que_8bits_por_char(self):
        texto = "aaaaaaaabbbbccd"
        cod = construir_codigos(texto)
        self.assertLess(len(codificar(texto, cod)), len(texto) * 8)

    def test_simbolo_unico(self):
        cod = construir_codigos("zzz")
        self.assertEqual(cod, {"z": "0"})
        self.assertEqual(decodificar(codificar("zzz", cod), cod), "zzz")

    def test_deterministico(self):
        self.assertEqual(construir_codigos("mississippi"), construir_codigos("mississippi"))

    def test_erros(self):
        with self.assertRaises(ValueError):
            construir_codigos("")
        cod = construir_codigos("abc")
        with self.assertRaises(ValueError):
            codificar("x", cod)
        with self.assertRaises(ValueError):
            decodificar("2", cod)
        with self.assertRaises(ValueError):
            decodificar("0", {"a": "00", "b": "01", "c": "10"})


if __name__ == "__main__":
    unittest.main()
