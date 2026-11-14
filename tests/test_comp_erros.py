import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from comp_erros import formatar_erro, formatar_erros, rotulo_do_erro
from comp_lexer import ErroLexico, ErroMini
from comp_parser import ErroSintaxe, parse
from comp_semantica import analisar
from comp_tipos import verificar
from comp_vm import ErroExecucao


def captura(fonte):
    try:
        parse(fonte)
    except ErroMini as e:
        return e
    raise AssertionError("esperava erro")


class TestErros(unittest.TestCase):
    def test_erro_de_sintaxe_com_seta(self):
        fonte = "var x = 1;\nvar y = 2\nvar z = 3;"
        saida = formatar_erro(fonte, captura(fonte), "prog.mini")
        self.assertEqual(saida.splitlines(), [
            "prog.mini:3:1: erro de sintaxe: esperado ';', encontrado 'var'",
            "  3 | var z = 3;",
            "    | ^^^"])

    def test_seta_na_coluna_certa(self):
        fonte = "print(1 @ 2);"
        e = captura(fonte)
        linhas = formatar_erro(fonte, e).splitlines()
        self.assertEqual(linhas[0], "<mini>:1:9: erro léxico: caractere inesperado '@'")
        self.assertEqual(linhas[1], "  1 | print(1 @ 2);")
        self.assertEqual(linhas[2], "    |         ^")

    def test_tamanho_do_token_vira_sublinhado(self):
        fonte = "var x = 12abc;"
        linhas = formatar_erro(fonte, captura(fonte)).splitlines()
        self.assertEqual(linhas[2], "    |         ^^^^^")

    def test_numero_de_linha_com_dois_digitos_alinha_margem(self):
        fonte = "\n" * 9 + "x = ;"
        linhas = formatar_erro(fonte, captura(fonte)).splitlines()
        self.assertEqual(linhas[1], "  10 | x = ;")
        self.assertEqual(linhas[2], "     |     ^")

    def test_erro_semantico(self):
        fonte = "var a = 1;\nprint(b);"
        e = analisar(parse(fonte)).erros[0]
        saida = formatar_erro(fonte, e)
        self.assertIn("erro semântico: variável 'b' não declarada", saida)
        self.assertEqual(saida.splitlines()[2], "    |       ^")

    def test_redeclaracao_e_semantico(self):
        e = analisar(parse("var a = 1; var a = 2;")).erros[0]
        self.assertEqual(rotulo_do_erro(e), "erro semântico")

    def test_erro_de_tipo(self):
        fonte = "var x = 1 + true;"
        e = verificar(parse(fonte))[0]
        self.assertIn("erro de tipo:", formatar_erro(fonte, e))

    def test_sem_posicao_so_cabecalho(self):
        self.assertEqual(formatar_erro("x", ErroExecucao("divisão por zero")),
                         "<mini>: erro de execução: divisão por zero")

    def test_tabulacao_alinha_seta(self):
        fonte = "\tprint(1 @ 2);"
        linhas = formatar_erro(fonte, captura(fonte)).splitlines()
        self.assertEqual(linhas[1], "  1 |     print(1 @ 2);")
        self.assertEqual(linhas[2].index("^"), linhas[1].index("@"))

    def test_erro_no_fim_do_arquivo(self):
        fonte = "while (true) {"
        linhas = formatar_erro(fonte, captura(fonte)).splitlines()
        self.assertIn("fim do arquivo", linhas[0])
        self.assertEqual(linhas[2], "    |               ^")

    def test_linha_alem_do_fim(self):
        fonte = "x = 1;\n"
        e = ErroSintaxe("esperado algo", 2, 1)
        self.assertEqual(formatar_erro(fonte, e).splitlines()[1], "  2 | ")

    def test_varios_erros_ordenados_com_resumo(self):
        fonte = "a = 1;\nb = 2;\nprint(c);"
        erros = analisar(parse(fonte)).erros
        saida = formatar_erros(fonte, list(reversed(erros)))
        self.assertLess(saida.index("<mini>:1:"), saida.index("<mini>:3:"))
        self.assertTrue(saida.endswith("3 erros"))
        self.assertTrue(formatar_erros(fonte, erros[:1]).endswith("1 erro"))

    def test_rotulo_generico(self):
        self.assertEqual(rotulo_do_erro(ErroMini("x")), "erro")
        self.assertEqual(rotulo_do_erro(ErroLexico("x")), "erro léxico")


if __name__ == "__main__":
    unittest.main()
