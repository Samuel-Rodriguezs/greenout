import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from comp_simbolos import ErroRedeclaracao, Simbolo, TabelaSimbolos


def var(nome, tipo="int", pos=(1, 1)):
    return Simbolo(nome, "var", tipo, pos)


class TestSimbolos(unittest.TestCase):
    def test_declarar_e_resolver(self):
        t = TabelaSimbolos()
        t.declarar(var("x"))
        self.assertEqual(t.resolver("x").tipo, "int")
        self.assertIsNone(t.resolver("y"))

    def test_escopo_interno_ve_externo(self):
        t = TabelaSimbolos()
        t.declarar(var("x"))
        t.entrar()
        self.assertIsNotNone(t.resolver("x"))
        self.assertIsNone(t.atual.resolver_local("x"))

    def test_sombreamento(self):
        t = TabelaSimbolos()
        t.declarar(var("x", "int"))
        t.entrar()
        t.declarar(var("x", "bool"))
        self.assertEqual(t.resolver("x").tipo, "bool")
        t.sair()
        self.assertEqual(t.resolver("x").tipo, "int")

    def test_redeclaracao_no_mesmo_escopo(self):
        t = TabelaSimbolos()
        t.declarar(var("x", pos=(2, 5)))
        with self.assertRaises(ErroRedeclaracao) as ctx:
            t.declarar(var("x", pos=(4, 9)))
        self.assertEqual((ctx.exception.linha, ctx.exception.coluna), (4, 9))
        self.assertIn("linha 2", ctx.exception.mensagem)

    def test_variavel_do_bloco_some_ao_sair(self):
        t = TabelaSimbolos()
        t.entrar("if")
        t.declarar(var("tmp"))
        t.sair()
        self.assertIsNone(t.resolver("tmp"))

    def test_sair_do_global_falha(self):
        with self.assertRaises(RuntimeError):
            TabelaSimbolos().sair()

    def test_funcao_aridade(self):
        s = Simbolo("f", "func", "int", params=("int", "bool"))
        self.assertEqual(s.aridade, 2)

    def test_profundidade_e_caminho(self):
        t = TabelaSimbolos()
        t.entrar("f")
        e = t.entrar("while")
        self.assertEqual(e.profundidade, 2)
        self.assertEqual(e.caminho(), "global/f/while")

    def test_todos_percorre_arvore(self):
        t = TabelaSimbolos()
        t.declarar(Simbolo("f", "func", "void"))
        t.entrar("f")
        t.declarar(Simbolo("a", "param", "int"))
        t.sair()
        t.entrar("main")
        t.declarar(var("z"))
        self.assertEqual([(c, s.nome) for c, s in t.todos()],
                         [("global", "f"), ("global/f", "a"), ("global/main", "z")])


if __name__ == "__main__":
    unittest.main()
