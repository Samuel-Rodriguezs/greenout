import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from so_shell import Comando, ErroSintaxe, Pipeline, Redirecionamento, Shell, parse, tokenizar

NOMES = b"ana\nbia\nana\ncarlos\nbia\nana\n"


def novo() -> Shell:
    sh = Shell()
    sh.sistema.arquivos["nomes.txt"] = bytearray(NOMES)
    return sh


class TestParser(unittest.TestCase):
    def test_tokens_com_aspas(self):
        self.assertEqual(
            tokenizar("echo 'a  b' \"c d\"e"),
            [("palavra", "echo"), ("palavra", "a  b"), ("palavra", "c de")],
        )

    def test_operadores_colados(self):
        self.assertEqual(
            tokenizar("a|b>f;c&&d"),
            [("palavra", "a"), ("op", "|"), ("palavra", "b"), ("op", ">"), ("palavra", "f"),
             ("op", ";"), ("palavra", "c"), ("op", "&&"), ("palavra", "d")],
        )

    def test_estrutura(self):
        ast = parse("cat < in | grep x > out; echo $? && true")
        self.assertEqual([c for c, _ in ast], [";", ";", "&&"])
        self.assertEqual(
            ast[0][1],
            Pipeline(
                [
                    Comando(["cat"], [Redirecionamento("<", "in")]),
                    Comando(["grep", "x"], [Redirecionamento(">", "out")]),
                ]
            ),
        )
        self.assertEqual(ast[2][1].comandos[0].argv, ["true"])

    def test_redirecionamento_de_erro(self):
        (_, p), = parse("cmd 2> e 2>&1")
        self.assertEqual(
            p.comandos[0].redirs, [Redirecionamento("2>", "e"), Redirecionamento("2>&1")]
        )

    def test_erros_de_sintaxe(self):
        for linha in ("echo a |", "| echo", "echo >", "echo 'abc", 'echo "abc', "a;;b", "a &&"):
            with self.subTest(linha=linha):
                with self.assertRaises(ErroSintaxe):
                    parse(linha)

    def test_linha_vazia_e_ponto_e_virgula_final(self):
        self.assertEqual(parse(""), [])
        self.assertEqual(len(parse("echo a;")), 1)


class TestExecucao(unittest.TestCase):
    def test_pipeline_sort_uniq(self):
        sh = novo()
        self.assertEqual(sh.executar("cat nomes.txt | sort | uniq -c"), 0)
        self.assertEqual(sh.saida(), "      3 ana\n      2 bia\n      1 carlos\n")

    def test_sort_numerico(self):
        sh = novo()
        sh.executar("sort nomes.txt | uniq -c | sort -n")
        self.assertEqual(sh.saida(), "      1 carlos\n      2 bia\n      3 ana\n")

    def test_pipeline_longo_propaga_eof(self):
        sh = novo()
        sh.executar("echo a | cat | cat | wc -c")
        self.assertEqual(sh.saida(), "2\n")

    def test_redirecionar_entrada(self):
        sh = novo()
        sh.executar("grep -c ana < nomes.txt")
        self.assertEqual(sh.saida(), "3\n")

    def test_redirecionar_saida_e_anexar(self):
        sh = novo()
        sh.executar("echo oi > a; cat a")
        self.assertEqual(sh.saida(), "oi\n")
        sh.executar("echo x >> a; cat a")
        self.assertEqual(sh.saida(), "oi\noi\nx\n")
        self.assertEqual(bytes(sh.sistema.arquivos["a"]), b"oi\nx\n")

    def test_conectores_e_status(self):
        sh = novo()
        sh.executar("false || echo ok")
        sh.executar("true && echo a && false || echo b")
        self.assertEqual(sh.saida(), "ok\na\nb\n")
        sh.executar("false; echo $?")
        self.assertEqual(sh.saida().splitlines()[-1], "1")
        sh.executar("echo '$?'")
        self.assertEqual(sh.saida().splitlines()[-1], "$?")

    def test_status_do_pipeline_e_o_do_ultimo(self):
        sh = novo()
        self.assertEqual(sh.executar("grep zzz nomes.txt | wc -l"), 0)
        self.assertEqual(sh.saida(), "0\n")
        self.assertEqual(sh.executar("grep zzz nomes.txt"), 1)

    def test_erro_em_stderr_e_2_para_1(self):
        sh = novo()
        self.assertEqual(sh.executar("cat naoexiste"), 1)
        self.assertEqual(sh.erro(), "cat: naoexiste: arquivo inexistente\n")
        sh.executar("cat naoexiste 2>&1 | wc -l")
        self.assertEqual(sh.saida(), "1\n")

    def test_stderr_para_arquivo(self):
        sh = novo()
        sh.executar("cat naoexiste 2> erros")
        self.assertEqual(bytes(sh.sistema.arquivos["erros"]), b"cat: naoexiste: arquivo inexistente\n")
        self.assertEqual(sh.erro(), "")

    def test_comando_desconhecido_e_entrada_inexistente(self):
        sh = novo()
        self.assertEqual(sh.executar("xyz"), 127)
        self.assertIn("comando não encontrado", sh.erro())
        self.assertEqual(sh.executar("cat < fantasma"), 1)

    def test_head_tail_wc(self):
        sh = novo()
        sh.executar("head -n 2 nomes.txt; tail -n 2 nomes.txt; wc nomes.txt")
        self.assertEqual(sh.saida(), "ana\nbia\nbia\nana\n6 6 27\n")

    def test_grep_v_i(self):
        sh = novo()
        sh.executar("grep -v ana nomes.txt | grep -i B")
        self.assertEqual(sh.saida(), "bia\nbia\n")

    def test_tee_ls_rm(self):
        sh = novo()
        sh.executar("echo -n oi | tee copia")
        self.assertEqual(sh.saida(), "oi")
        self.assertEqual(bytes(sh.sistema.arquivos["copia"]), b"oi")
        sh.executar("ls")
        self.assertTrue(sh.saida().endswith("copia\nnomes.txt\n"))
        self.assertEqual(sh.executar("rm copia"), 0)
        self.assertEqual(sh.executar("rm copia"), 1)

    def test_aspas_preservam_espacos(self):
        sh = novo()
        sh.executar('echo "a  b" c')
        self.assertEqual(sh.saida(), "a  b c\n")

    def test_stdin_do_console(self):
        sh = novo()
        sh.sistema.stdin += b"teclado"
        sh.executar("cat")
        self.assertEqual(sh.saida(), "teclado")

    def test_erro_de_sintaxe_no_executar(self):
        sh = novo()
        self.assertEqual(sh.executar("echo a |"), 2)
        self.assertIn("erro de sintaxe", sh.erro())

    def test_nao_vaza_descritores_no_shell(self):
        sh = novo()
        sh.executar("echo a | cat | wc -l")
        self.assertEqual(sorted(sh.tabela.fds), [0, 1, 2])


if __name__ == "__main__":
    unittest.main()
