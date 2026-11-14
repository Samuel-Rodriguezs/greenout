import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from comp_repl import Repl


class TestRepl(unittest.TestCase):
    def setUp(self):
        self.r = Repl()

    def test_expressao_imprime_valor(self):
        self.assertEqual(self.r.processar("1 + 2 * 3"), "7")
        self.assertEqual(self.r.processar("1 < 2"), "true")
        self.assertEqual(self.r.processar("-7 / 2"), "-3")

    def test_comando_com_saida(self):
        self.assertEqual(self.r.processar("print(5); print(true);"), "5\ntrue")

    def test_variaveis_persistem(self):
        self.assertEqual(self.r.processar("var x = 10;"), "")
        self.assertEqual(self.r.processar("x = x * 2;"), "")
        self.assertEqual(self.r.processar("x + 1"), "21")
        self.assertEqual(self.r.processar(":vars"), "x: int = 20")

    def test_variavel_booleana(self):
        self.r.processar("var ok = 3 > 2;")
        self.assertEqual(self.r.processar("!ok"), "false")
        self.assertEqual(self.r.processar(":vars"), "ok: bool = true")

    def test_funcao_multilinha_com_continuacao(self):
        self.assertEqual(self.r.processar("func fat(n: int) -> int {"), "")
        self.assertTrue(self.r.aguardando_continuacao)
        self.assertEqual(self.r.processar("    if (n <= 1) { return 1; }"), "")
        self.assertEqual(self.r.processar("    return n * fat(n - 1);"), "")
        self.assertEqual(self.r.processar("}"), "")
        self.assertFalse(self.r.aguardando_continuacao)
        self.assertEqual(self.r.processar("fat(6)"), "720")
        self.assertEqual(self.r.processar(":funcoes"), "fat(n: int) -> int")

    def test_funcao_void_como_expressao(self):
        self.r.processar("func ola(n: int) { print(n + 1); }")
        self.assertEqual(self.r.processar("ola(1)"), "2")

    def test_funcao_usa_variavel_do_repl_so_via_parametro(self):
        self.r.processar("var g = 1;")
        self.r.processar("func f() -> int { return g; }")
        # g não é visível dentro de funções (regra de Mini): erro e função não registrada
        self.assertEqual(self.r.processar(":funcoes"), "(nenhuma função)")

    def test_erro_semantico_com_seta_e_estado_preservado(self):
        self.r.processar("var a = 1;")
        saida = self.r.processar("print(b);")
        self.assertEqual(saida.splitlines(), [
            "<repl>:1:7: erro semântico: variável 'b' não declarada",
            "  1 | print(b);",
            "    |       ^",
            "1 erro"])
        self.assertEqual(self.r.processar("a"), "1")

    def test_erro_de_sintaxe(self):
        saida = self.r.processar("var x = ;")
        self.assertIn("erro de sintaxe: esperado expressão", saida)
        self.assertEqual(self.r.processar(":vars"), "(nenhuma variável)")

    def test_erro_lexico_imediato(self):
        saida = self.r.processar("1 @ 2")
        self.assertIn("erro léxico", saida)
        self.assertFalse(self.r.aguardando_continuacao)

    def test_erro_de_tipo(self):
        self.assertIn("erro de tipo: operador '+' exige int", self.r.processar("1 + true"))
        self.r.processar("var n = 1;")
        self.assertIn("atribuição de bool a 'n' do tipo int", self.r.processar("n = false;"))

    def test_redeclaracao_variavel(self):
        self.r.processar("var x = 1;")
        self.assertIn("já declarado", self.r.processar("var x = 2;"))
        self.assertEqual(self.r.processar("x"), "1")

    def test_erro_de_execucao_nao_altera_estado(self):
        self.r.processar("var z = 0;")
        saida = self.r.processar("z = 5; print(1 / (z - 5));")
        self.assertIn("erro de execução: divisão por zero", saida)
        self.assertEqual(self.r.processar("z"), "0")

    def test_comentario_de_bloco_pede_continuacao(self):
        self.assertEqual(self.r.processar("/* abre"), "")
        self.assertTrue(self.r.aguardando_continuacao)
        self.assertEqual(self.r.processar("fecha */ 4 + 4"), "8")

    def test_linha_vazia_e_comentario(self):
        self.assertEqual(self.r.processar(""), "")
        self.assertEqual(self.r.processar("   "), "")
        self.assertEqual(self.r.processar("// nada"), "")

    def test_ast_e_tac(self):
        self.assertEqual(self.r.processar(":ast var x = 1;").splitlines(),
                         ["Programa", "  Var(nome='x')", "    Num(valor=1)"])
        self.assertEqual(self.r.processar(":tac var x = 1 + 2;").splitlines(),
                         ["func main():", "    %t1 = 1 + 2", "    x = %t1", "    return"])
        self.assertIn("erro de sintaxe", self.r.processar(":ast var"))

    def test_limpar_ajuda_desconhecido_e_sair(self):
        self.r.processar("var x = 1;")
        self.assertEqual(self.r.processar(":limpar"), "estado limpo")
        self.assertEqual(self.r.processar(":vars"), "(nenhuma variável)")
        self.assertIn(":sair", self.r.processar(":ajuda"))
        self.assertIn("desconhecido", self.r.processar(":xpto"))
        self.assertFalse(self.r.encerrado)
        self.r.processar(":sair")
        self.assertTrue(self.r.encerrado)

    def test_sessao_transcricao(self):
        r = Repl()
        transcricao = r.sessao([
            "var i = 0;",
            "while (i < 2) {",
            "  print(i);",
            "  i = i + 1;",
            "}",
            "i * 10",
            ":sair",
            "ignorada",
        ])
        self.assertEqual(transcricao.splitlines(), [
            "mini> var i = 0;",
            "mini> while (i < 2) {",
            "...>   print(i);",
            "...>   i = i + 1;",
            "...> }",
            "0",
            "1",
            "mini> i * 10",
            "20",
            "mini> :sair",
            "tchau",
        ])


if __name__ == "__main__":
    unittest.main()
