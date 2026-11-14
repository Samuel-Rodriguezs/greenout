import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from comp_ast import Atrib, Binario, Chamada, ExprStmt, Imprimir, Nome, Num
from comp_parser import parse
from comp_visitor import (Transformador, Visitante, contem, eh_pura, filhos,
                          percorrer)

FONTE = "func f(a: int) -> int { return a + 1; } var x = f(2) * 3; print(x);"


class ContaNomes(Visitante):
    def __init__(self):
        self.nomes = []

    def visitar_Nome(self, no):
        self.nomes.append(no.nome)


class TestVisitor(unittest.TestCase):
    def test_filhos_ordem(self):
        e = Binario("+", Num(1), Nome("a"))
        self.assertEqual(filhos(e), [Num(1), Nome("a")])
        self.assertEqual(filhos(Num(1)), [])

    def test_percorrer_pre_ordem(self):
        e = Binario("+", Num(1), Binario("*", Nome("a"), Num(2)))
        tipos = [type(n).__name__ for n in percorrer(e)]
        self.assertEqual(tipos, ["Binario", "Num", "Binario", "Nome", "Num"])

    def test_visitante_com_metodo_especifico(self):
        v = ContaNomes()
        v.visitar(parse(FONTE))
        self.assertEqual(v.nomes, ["a", "x"])

    def test_contem_e_pureza(self):
        p = parse(FONTE)
        self.assertTrue(contem(p, Chamada))
        self.assertTrue(eh_pura(Binario("+", Num(1), Nome("a"))))
        self.assertFalse(eh_pura(Binario("+", Num(1), Chamada("f", []))))


class Incrementa(Transformador):
    def transformar_Num(self, no):
        return Num(no.valor + 1, pos=no.pos)


class RemovePrint(Transformador):
    def transformar_Imprimir(self, no):
        return None


class DuplicaAtrib(Transformador):
    def transformar_Atrib(self, no):
        return [no, ExprStmt(Nome(no.nome))]


class TestTransformador(unittest.TestCase):
    def test_transforma_sem_mutar_original(self):
        original = parse("var x = 1 + 2;")
        novo = Incrementa().transformar(original)
        self.assertEqual(novo, parse("var x = 2 + 3;"))
        self.assertEqual(original, parse("var x = 1 + 2;"))

    def test_preserva_posicao(self):
        novo = Incrementa().transformar(parse("\n  var x = 7;"))
        self.assertEqual(novo.itens[0].init.pos, (2, 11))

    def test_none_remove_da_lista(self):
        novo = RemovePrint().transformar(parse("var x = 1; print(x); print(2);"))
        self.assertEqual(len(novo.itens), 1)

    def test_lista_e_emendada(self):
        novo = DuplicaAtrib().transformar(parse("x = 1; { x = 2; }"))
        self.assertEqual(novo.itens[0], Atrib("x", Num(1)))
        self.assertEqual(novo.itens[1], ExprStmt(Nome("x")))
        self.assertEqual(len(novo.itens[2].stmts), 2)

    def test_generico_identidade(self):
        p = parse(FONTE)
        self.assertEqual(Transformador().transformar(p), p)
        self.assertIsNot(Transformador().transformar(p), p)

    def test_campo_opcional_none_preservado(self):
        p = parse("if (true) { print(1); }")
        self.assertIsNone(Transformador().transformar(p).itens[0].senao)
        self.assertIsInstance(Transformador().transformar(p).itens[0].entao.stmts[0], Imprimir)


if __name__ == "__main__":
    unittest.main()
