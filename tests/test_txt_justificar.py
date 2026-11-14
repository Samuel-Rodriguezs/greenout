import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from txt_justificar import centralizar, justificar, quebrar_linhas


class TestJustificar(unittest.TestCase):
    def test_quebra(self):
        self.assertEqual(quebrar_linhas("aaa bbb ccc", 7), ["aaa bbb", "ccc"])
        self.assertEqual(quebrar_linhas("  muitos   espaços  ", 20), ["muitos espaços"])

    def test_palavra_longa(self):
        self.assertEqual(quebrar_linhas("abcdefghij", 4), ["abcd", "efgh", "ij"])

    def test_vazio_e_largura_invalida(self):
        self.assertEqual(quebrar_linhas("", 10), [])
        with self.assertRaises(ValueError):
            quebrar_linhas("a", 0)

    def test_justificar_distribui_espacos(self):
        self.assertEqual(justificar("a bb ccc dddd", 10), ["a  bb  ccc", "dddd"])
        self.assertEqual(justificar("a b c dddd", 6), ["a  b c", "dddd"])

    def test_justificar_largura_exata(self):
        for linha in justificar("um texto qualquer para testar a justificação das linhas", 15)[:-1]:
            if " " in linha:
                self.assertEqual(len(linha), 15)

    def test_linha_unica_palavra(self):
        self.assertEqual(justificar("palavraqueseestende ok", 25), ["palavraqueseestende ok"])
        self.assertEqual(justificar("abcdefgh x", 8), ["abcdefgh", "x"])

    def test_centralizar(self):
        self.assertEqual(centralizar("ab", 6), ["  ab"])


if __name__ == "__main__":
    unittest.main()
