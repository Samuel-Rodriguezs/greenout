import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from lang_sexpr import ErroSexpr, compacto, formatar, formatar_texto, ler

FAT = "(define (fat n) (if (<= n 1) 1 (* n (fat (- n 1)))))"


class TestSexpr(unittest.TestCase):
    def test_ler(self):
        self.assertEqual(ler("(a (b c) d) e"), [["a", ["b", "c"], "d"], "e"])
        self.assertEqual(ler("()"), [[]])
        self.assertEqual(ler(""), [])

    def test_ler_string_e_comentario(self):
        self.assertEqual(ler('(f "a (b)" ; x\n c)'), [["f", '"a (b)"', "c"]])

    def test_compacto_normaliza_espacos(self):
        self.assertEqual(compacto(ler("(  a   (b\n c) )")[0]), "(a (b c))")

    def test_cabe_na_linha(self):
        self.assertEqual(formatar(ler(FAT)[0], largura=80), FAT)

    def test_quebra(self):
        saida = formatar(ler(FAT)[0], largura=30)
        self.assertEqual(
            saida,
            "(define (fat n)\n"
            "        (if (<= n 1)\n"
            "            1\n"
            "            (* n\n"
            "               (fat (- n 1)))))",
        )
        for linha in saida.splitlines():
            self.assertLessEqual(len(linha), 36)

    def test_formatar_preserva_semantica(self):
        for largura in (10, 20, 40, 100):
            self.assertEqual(ler(formatar(ler(FAT)[0], largura)), ler(FAT))

    def test_cabeca_lista(self):
        x = ler("((a b) (c d) (e f))")[0]
        self.assertEqual(formatar(x, 10), "((a b)\n (c d)\n (e f))")

    def test_formatar_texto_varias(self):
        self.assertEqual(formatar_texto("(a  b)\n(c)"), "(a b)\n\n(c)")

    def test_erros(self):
        for t in ["(a b", ")", "(a))", '(a "b)']:
            with self.assertRaises(ErroSexpr, msg=t):
                ler(t)


if __name__ == "__main__":
    unittest.main()
