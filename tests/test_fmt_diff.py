import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fmt_diff import ErroPatch, aplicar, gerar, parse_patch

A = "".join(f"linha {i}\n" for i in range(1, 21))


class TestFmtDiff(unittest.TestCase):
    def test_iguais(self):
        self.assertEqual(gerar(A, A), "")

    def test_formato(self):
        novo = A.replace("linha 10\n", "DEZ\n")
        d = gerar(A, novo, "x.txt", "y.txt")
        esperado = ("--- x.txt\n+++ y.txt\n@@ -7,7 +7,7 @@\n linha 7\n linha 8\n linha 9\n-linha 10\n+DEZ\n"
                    " linha 11\n linha 12\n linha 13\n")
        self.assertEqual(d, esperado)
        self.assertEqual(aplicar(A, d), novo)

    def test_insercao_remocao_inicio_e_fim(self):
        for novo in ["zero\n" + A, A + "fim\n", A.split("\n", 1)[1], A.rsplit("linha 20\n", 1)[0]]:
            with self.subTest(novo=novo[:12]):
                self.assertEqual(aplicar(A, gerar(A, novo)), novo)

    def test_varios_hunks(self):
        linhas = A.split("\n")
        linhas[1] = "dois"
        linhas[18] = "dezenove"
        novo = "\n".join(linhas)
        d = gerar(A, novo)
        self.assertEqual(len(parse_patch(d)), 2)
        self.assertEqual(aplicar(A, d), novo)

    def test_arquivo_vazio(self):
        self.assertEqual(aplicar("", gerar("", "a\nb\n")), "a\nb\n")
        self.assertEqual(aplicar("a\nb\n", gerar("a\nb\n", "")), "")

    def test_reverso(self):
        novo = A.replace("linha 5\n", "cinco\nextra\n")
        self.assertEqual(aplicar(novo, gerar(A, novo), reverso=True), A)

    def test_aleatorio(self):
        rnd = random.Random(7)
        for _ in range(60):
            a = "".join(f"{rnd.choice('abcde')}\n" for _ in range(rnd.randint(0, 25)))
            b = "".join(f"{rnd.choice('abcde')}\n" for _ in range(rnd.randint(0, 25)))
            d = gerar(a, b)
            self.assertEqual(aplicar(a, d) if d else a, b if d else a)
            if d:
                self.assertEqual(aplicar(b, d, reverso=True), a)

    def test_conflito(self):
        d = gerar(A, A.replace("linha 10\n", "DEZ\n"))
        with self.assertRaises(ErroPatch):
            aplicar(A.replace("linha 9\n", "outra\n"), d)
        with self.assertRaises(ErroPatch):
            aplicar("curto\n", d)

    def test_patch_malformado(self):
        for ruim in ["", "lixo\n", "@@ -1,1 +1,1 @@\n-a\n", "@@ -1,1 +1,1 @@\nxa\n+b\n",
                     "@@ -1,2 +1,1 @@\n a\n"]:
            with self.subTest(ruim=ruim):
                with self.assertRaises(ErroPatch):
                    aplicar("a\n", ruim)

    def test_sem_quebra_final(self):
        with self.assertRaises(ErroPatch):
            gerar("a", "b\n")


if __name__ == "__main__":
    unittest.main()
