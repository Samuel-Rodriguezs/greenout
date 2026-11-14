import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fmt_tabela_ascii import ErroTabelaAscii, formatar, largura


class TestFmtTabelaAscii(unittest.TestCase):
    def test_basico(self):
        t = formatar(["nome", "qtd"], [["maçã", 3], ["banana", 12]])
        esperado = "\n".join([
            "+--------+-----+",
            "|  nome  | qtd |",
            "+--------+-----+",
            "| maçã   |   3 |",
            "| banana |  12 |",
            "+--------+-----+",
        ])
        self.assertEqual(t, esperado)

    def test_alinhamentos_explicitos(self):
        t = formatar(["a", "b"], [["x", "y"]], ["d", "c"])
        self.assertIn("| x | y |", t)
        t2 = formatar(["abcd", "efgh"], [["x", "y"]], ["d", "c"])
        self.assertIn("|    x |  y   |", t2)

    def test_truncar(self):
        t = formatar(["col"], [["abcdefghij"]], largura_max=5)
        self.assertIn("| abcd… |", t)

    def test_estilo_simples(self):
        t = formatar(["a", "bb"], [[1, "x"], [22, "y"]], estilo="simples")
        self.assertEqual(t.split("\n"), [" a  bb", "--  --", " 1  x", "22  y"])

    def test_largura_unicode(self):
        self.assertEqual(largura("日本"), 4)
        self.assertEqual(largura("é"), 1)
        t = formatar(["k"], [["日本"], ["ab"]])
        linhas = t.split("\n")
        self.assertEqual({largura(l) for l in linhas}, {largura(linhas[0])})

    def test_sem_linhas_e_quebra(self):
        self.assertEqual(len(formatar(["a", "b"], []).split("\n")), 4)
        self.assertIn("a b", formatar(["x"], [["a\nb"]]))

    def test_invalidos(self):
        with self.assertRaises(ErroTabelaAscii):
            formatar([], [])
        with self.assertRaises(ErroTabelaAscii):
            formatar(["a"], [["1", "2"]])
        with self.assertRaises(ErroTabelaAscii):
            formatar(["a"], [], ["z"])
        with self.assertRaises(ErroTabelaAscii):
            formatar(["a"], [], estilo="xyz")
        with self.assertRaises(ErroTabelaAscii):
            formatar(["a"], [], largura_max=0)


if __name__ == "__main__":
    unittest.main()
