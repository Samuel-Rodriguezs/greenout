import dataclasses
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from comp_ast import (Atrib, Binario, Bloco, Bool, Chamada, EXPRESSOES, Funcao,
                      Num, Nome, No, Param, Programa, Retorno, Se, Var)


class TestAst(unittest.TestCase):
    def test_posicao_nao_afeta_igualdade(self):
        self.assertEqual(Num(1, pos=(1, 1)), Num(1, pos=(9, 9)))
        self.assertNotEqual(Num(1), Num(2))

    def test_posicao_padrao_e_nomeada(self):
        n = Nome("x", pos=(3, 4))
        self.assertEqual(n.pos, (3, 4))
        self.assertEqual(Nome("y").pos, (0, 0))

    def test_estrutura_aninhada(self):
        e = Binario("+", Num(1), Binario("*", Nome("a"), Num(2)))
        self.assertEqual(e.dir.esq, Nome("a"))

    def test_se_senao_opcional(self):
        s = Se(Bool(True), Bloco([]))
        self.assertIsNone(s.senao)

    def test_var_tipo_opcional(self):
        self.assertIsNone(Var("x", Num(1)).tipo)
        self.assertEqual(Var("x", Num(1), "int").tipo, "int")

    def test_programa_separa_funcoes_e_comandos(self):
        f = Funcao("f", [Param("a", "int")], "int", Bloco([Retorno(Nome("a"))]))
        p = Programa([f, Atrib("x", Num(1)), Chamada("f", [Num(1)])])
        self.assertEqual(p.funcoes(), [f])
        self.assertEqual(len(p.comandos()), 2)

    def test_todos_os_nos_sao_dataclasses_de_no(self):
        for cls in EXPRESSOES:
            self.assertTrue(dataclasses.is_dataclass(cls))
            self.assertTrue(issubclass(cls, No))

    def test_listas_nao_sao_compartilhadas(self):
        a, b = Bloco([]), Bloco([])
        a.stmts.append(Num(1))
        self.assertEqual(b.stmts, [])


if __name__ == "__main__":
    unittest.main()
