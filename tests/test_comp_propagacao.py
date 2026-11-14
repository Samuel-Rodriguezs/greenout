import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from comp_gerador import gerar
from comp_parser import parse
from comp_propagacao import propagar_constantes
from comp_vm import executar


def prop(fonte):
    return propagar_constantes(parse(fonte))


def roda(programa):
    return executar(gerar(programa)).saida


class TestPropagacao(unittest.TestCase):
    def test_sequencia_simples(self):
        self.assertEqual(prop("var a = 4; var b = a; print(a + b);"),
                         parse("var a = 4; var b = 4; print(4 + 4);"))

    def test_atribuicao_atualiza_valor(self):
        self.assertEqual(prop("var a = 1; a = 2; print(a);"),
                         parse("var a = 1; a = 2; print(2);"))

    def test_valor_desconhecido_apaga_constante(self):
        fonte = "func f() -> int { return 3; } var a = 1; a = f(); print(a);"
        self.assertEqual(prop(fonte), parse(fonte))

    def test_propaga_bool(self):
        self.assertEqual(prop("var c = true; if (c) { print(1); }"),
                         parse("var c = true; if (true) { print(1); }"))

    def test_atribuicao_usa_valor_propagado(self):
        self.assertEqual(prop("var a = 2; var b = 0; b = a * 5; print(b);"),
                         parse("var a = 2; var b = 0; b = 2 * 5; print(b);"))

    def test_if_juncao_igual(self):
        p = prop("var a = 0; var c = true; if (c) { a = 5; } else { a = 5; } print(a);")
        self.assertEqual(p.itens[-1], parse("print(5);").itens[0])

    def test_if_juncao_diferente(self):
        p = prop("var a = 0; var c = true; if (c) { a = 1; } else { a = 2; } print(a);")
        self.assertEqual(p.itens[-1], parse("print(a);").itens[0])

    def test_if_sem_else_so_um_caminho_altera(self):
        p = prop("var a = 0; var c = false; if (c) { a = 9; } print(a);")
        self.assertEqual(p.itens[-1], parse("print(a);").itens[0])

    def test_ramo_ve_valor_de_antes(self):
        p = prop("var a = 3; if (true) { print(a); }")
        self.assertEqual(p.itens[1].entao.stmts[0], parse("print(3);").itens[0])

    def test_while_esquece_variaveis_alteradas(self):
        fonte = "var i = 0; var k = 10; while (i < k) { i = i + 1; } print(i); print(k);"
        esperado = "var i = 0; var k = 10; while (i < 10) { i = i + 1; } print(i); print(10);"
        self.assertEqual(prop(fonte), parse(esperado))

    def test_while_nao_propaga_valor_inicial_para_dentro(self):
        p = prop("var s = 0; var i = 0; while (i < 3) { s = s + i; i = i + 1; } print(s);")
        corpo = p.itens[2].corpo.stmts
        self.assertEqual(corpo[0], parse("s = s + i;").itens[0])

    def test_sombreamento_restaurado(self):
        fonte = "var x = 1; { var x = 2; print(x); } print(x);"
        self.assertEqual(prop(fonte), parse("var x = 1; { var x = 2; print(2); } print(1);"))

    def test_sombreamento_desconhecido_esconde_constante(self):
        fonte = "func f() -> int { return 1; } var x = 1; { var x = f(); print(x); } print(x);"
        self.assertEqual(prop(fonte),
                         parse("func f() -> int { return 1; } var x = 1; { var x = f(); print(x); } print(1);"))

    def test_parametros_sao_desconhecidos(self):
        fonte = "func f(n: int) -> int { var k = 2; return n * k; }"
        self.assertEqual(prop(fonte), parse("func f(n: int) -> int { var k = 2; return n * 2; }"))

    def test_funcoes_nao_veem_constantes_do_main(self):
        fonte = "func f() -> int { var a = 1; return a; } var a = 5; print(f());"
        self.assertEqual(prop(fonte).itens[0].corpo.stmts[1].valor, parse("1;").itens[0].expr)

    def test_nao_altera_original(self):
        p = parse("var a = 1; print(a);")
        propagar_constantes(p)
        self.assertEqual(p, parse("var a = 1; print(a);"))

    def test_preserva_comportamento(self):
        fonte = """
        func g(n: int) -> int { var base = 10; var mult = 3; if (n > 2) { mult = 4; } return base * mult + n; }
        var a = 5; var b = a * 2; var flag = true; var total = 0; var i = 0;
        while (i < a) {
            if (flag) { total = total + b; } else { total = total - 1; }
            var b = i;
            total = total + b;
            i = i + 1;
        }
        flag = false;
        print(total); print(g(1)); print(g(7)); print(a); print(flag);
        """
        original = parse(fonte)
        self.assertEqual(roda(propagar_constantes(original)), roda(original))


if __name__ == "__main__":
    unittest.main()
