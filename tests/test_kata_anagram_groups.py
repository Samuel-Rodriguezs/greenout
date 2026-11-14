import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_anagram_groups import agrupar, maior_grupo


class TestKataAnagramGroups(unittest.TestCase):
    def test_vazio(self):
        self.assertEqual(agrupar([]), [])

    def test_sem_anagramas(self):
        self.assertEqual(agrupar(["casa", "mesa"]), [["casa"], ["mesa"]])

    def test_grupos(self):
        palavras = ["amor", "roma", "ramo", "mora", "casa", "saca"]
        self.assertEqual(agrupar(palavras), [["amor", "roma", "ramo", "mora"], ["casa", "saca"]])

    def test_ordem_de_primeira_aparicao(self):
        self.assertEqual(agrupar(["listen", "abc", "silent", "cab"]),
                         [["listen", "silent"], ["abc", "cab"]])

    def test_ignora_caixa_e_acentos(self):
        self.assertEqual(agrupar(["Ração", "caroa"]), [["Ração", "caroa"]])
        self.assertEqual(agrupar(["Ave", "eva"]), [["Ave", "eva"]])
        self.assertEqual(agrupar(["pé", "ep"]), [["pé", "ep"]])

    def test_minimo(self):
        palavras = ["amor", "roma", "casa"]
        self.assertEqual(agrupar(palavras, minimo=2), [["amor", "roma"]])

    def test_duplicatas_removidas(self):
        self.assertEqual(agrupar(["ab", "ba", "ab"]), [["ab", "ba"]])

    def test_ignora_vazias(self):
        self.assertEqual(agrupar(["", "!!", "a"]), [["a"]])

    def test_maior_grupo(self):
        self.assertEqual(maior_grupo(["amor", "roma", "ramo", "casa", "saca"]), ["amor", "roma", "ramo"])
        self.assertEqual(maior_grupo([]), [])

    def test_minimo_invalido(self):
        with self.assertRaises(ValueError):
            agrupar(["a"], minimo=0)


if __name__ == "__main__":
    unittest.main()
