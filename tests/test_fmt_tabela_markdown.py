import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fmt_tabela_markdown import ErroTabela, gerar_tabela, para_dicts, parse_tabela


class TestFmtTabelaMarkdown(unittest.TestCase):
    def test_basico(self):
        t = "| nome | idade |\n|------|------:|\n| Ana | 30 |\n| Bia | 25 |"
        cab, alin, regs = parse_tabela(t)
        self.assertEqual(cab, ["nome", "idade"])
        self.assertEqual(alin, ["esquerda", "direita"])
        self.assertEqual(regs, [{"nome": "Ana", "idade": "30"}, {"nome": "Bia", "idade": "25"}])

    def test_sem_barras_externas_e_centro(self):
        _, alin, regs = parse_tabela("a | b\n:-: | ---\n1 | 2")
        self.assertEqual(alin, ["centro", "esquerda"])
        self.assertEqual(regs, [{"a": "1", "b": "2"}])

    def test_pipe_escapado_e_celula_faltando(self):
        regs = para_dicts("| a | b |\n|---|---|\n| x\\|y |\n")
        self.assertEqual(regs, [{"a": "x|y", "b": ""}])

    def test_malformadas(self):
        for ruim in ["| a |", "| a | b |\n|---|\n| 1 | 2 |", "| a |\n| xx |\n| 1 |",
                     "| a |\n|---|\n| 1 | 2 |", "| a | |\n|---|---|"]:
            with self.subTest(ruim=ruim):
                with self.assertRaises(ErroTabela):
                    parse_tabela(ruim)

    def test_gerar_e_ida_e_volta(self):
        t = gerar_tabela(["nome", "n"], [["Ana", "1"], ["B|b", "22"]], ["esquerda", "direita"])
        self.assertEqual(para_dicts(t), [{"nome": "Ana", "n": "1"}, {"nome": "B|b", "n": "22"}])
        self.assertEqual(parse_tabela(t)[1], ["esquerda", "direita"])
        with self.assertRaises(ErroTabela):
            gerar_tabela(["a"], [["1", "2"]])


if __name__ == "__main__":
    unittest.main()
