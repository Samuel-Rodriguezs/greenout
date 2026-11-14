import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from comp_codigo_morto import eliminar_codigo_morto
from comp_gerador import gerar
from comp_parser import parse
from comp_vm import executar


def limpa(fonte):
    return eliminar_codigo_morto(parse(fonte))


def roda(programa):
    return executar(gerar(programa)).saida


class TestCodigoMorto(unittest.TestCase):
    def test_apos_return(self):
        p = limpa("func f() -> int { return 1; print(2); var x = 3; } print(f());")
        self.assertEqual(p, parse("func f() -> int { return 1; } print(f());"))

    def test_apos_if_que_retorna_nos_dois_ramos(self):
        p = limpa("func f(a: bool) -> int { if (a) { return 1; } else { return 2; } print(9); } print(f(true));")
        self.assertEqual(p, parse("func f(a: bool) -> int { if (a) { return 1; } else { return 2; } } print(f(true));"))

    def test_if_literal(self):
        self.assertEqual(limpa("if (true) { print(1); } else { print(2); }"), parse("print(1);"))
        self.assertEqual(limpa("if (false) { print(1); } else { print(2); }"), parse("print(2);"))
        self.assertEqual(limpa("if (false) { print(1); }"), parse(""))

    def test_while_false(self):
        self.assertEqual(limpa("while (false) { print(1); } print(2);"), parse("print(2);"))

    def test_while_true_permanece(self):
        self.assertEqual(limpa("while (true) { print(1); }"), parse("while (true) { print(1); }"))

    def test_expressao_pura_como_comando(self):
        self.assertEqual(limpa("var a = 1; a; 1 + 2; print(a);"), parse("var a = 1; print(a);"))

    def test_expressao_com_chamada_permanece(self):
        fonte = "func f() -> int { print(5); return 1; } f();"
        self.assertEqual(limpa(fonte), parse(fonte))

    def test_if_vazio(self):
        self.assertEqual(limpa("var a = true; if (a) { } else { } print(1);"),
                         parse("print(1);"))

    def test_variavel_nunca_lida(self):
        self.assertEqual(limpa("var x = 1; var y = 2; x = 5; print(y);"), parse("var y = 2; print(y);"))

    def test_variavel_nao_lida_com_efeito_mantem_chamada(self):
        fonte = "func f() -> int { print(7); return 1; } var x = f(); x = f();"
        p = limpa(fonte)
        self.assertEqual(p, parse("func f() -> int { print(7); return 1; } f(); f();"))
        self.assertEqual(roda(p), ["7", "7"])

    def test_variaveis_em_cascata(self):
        # b só é lida para calcular a, que ninguém lê
        self.assertEqual(limpa("var b = 2; var a = b + 1;"), parse(""))

    def test_funcao_inalcancavel(self):
        fonte = """
        func usada() -> int { return aux(); } func aux() -> int { return 1; }
        func morta() -> int { return 2; } func morta2() -> int { return morta(); }
        print(usada());
        """
        p = limpa(fonte)
        self.assertEqual([f.nome for f in p.funcoes()], ["usada", "aux"])

    def test_recursao_inalcancavel_removida(self):
        p = limpa("func r(n: int) -> int { return r(n - 1); } print(1);")
        self.assertEqual(p.funcoes(), [])

    def test_bloco_com_var_nao_e_achatado(self):
        fonte = "var x = 1; { var x = 2; print(x); } print(x);"
        self.assertEqual(limpa(fonte), parse(fonte))

    def test_bloco_sem_var_e_achatado(self):
        self.assertEqual(limpa("var a = 1; { print(a); } { { print(a); } }"),
                         parse("var a = 1; print(a); print(a);"))

    def test_preserva_comportamento(self):
        fonte = """
        func fib(n: int) -> int { if (n < 2) { return n; } return fib(n - 1) + fib(n - 2); }
        func lixo() -> int { return 0; }
        var i = 0; var sobra = 10; var total = 0;
        while (i < 8) {
            if (false) { print(999); }
            total = total + fib(i);
            i = i + 1;
            sobra = sobra + 1;
        }
        print(total);
        if (true) { print(i); } else { print(-1); }
        """
        original = parse(fonte)
        self.assertEqual(roda(eliminar_codigo_morto(original)), roda(original))

    def test_idempotente(self):
        p = limpa("var u = 1; if (true) { print(1); } while (false) { }")
        self.assertEqual(eliminar_codigo_morto(p), p)


if __name__ == "__main__":
    unittest.main()
