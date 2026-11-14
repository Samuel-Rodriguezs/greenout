import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bd_sql_parser import parse
from bd_volcano import (Distinto, ErroExecucao, Filtro, JuncaoLoopAninhado, Limite,
                        Ordenacao, Projecao, Scan, avaliar)

USUARIOS = [(1, "ana", 30), (2, "bia", None), (3, "caio", 17), (4, "ana", 45)]
PEDIDOS = [(10, 1, 5.0), (11, 1, 7.5), (12, 3, 1.0), (13, 9, 2.0)]


def usuarios():
    return Scan("Usuarios", ["id", "nome", "idade"], USUARIOS, "u")


def pedidos():
    return Scan("pedidos", ["id", "uid", "valor"], PEDIDOS, "p")


def expr(texto):
    return parse(f"SELECT {texto} FROM t").itens[0].expr


def onde(texto):
    return parse(f"SELECT * FROM t WHERE {texto}").where


class TestAvaliador(unittest.TestCase):
    ESQ = [("u", "id"), ("u", "nome"), ("u", "idade")]

    def av(self, texto, linha=(1, "ana", 30)):
        return avaliar(expr(texto), self.ESQ, linha)

    def test_aritmetica(self):
        self.assertEqual(self.av("idade + 1 * 2"), 32)
        self.assertEqual(self.av("7 / 2"), 3)
        self.assertEqual(self.av("7.0 / 2"), 3.5)
        self.assertEqual(self.av("7 % 4"), 3)
        self.assertEqual(self.av("-idade"), -30)

    def test_divisao_por_zero(self):
        with self.assertRaises(ErroExecucao):
            self.av("1 / 0")

    def test_null_propaga(self):
        self.assertIsNone(self.av("idade + 1", (1, "x", None)))
        self.assertIsNone(self.av("idade = 3", (1, "x", None)))
        self.assertIsNone(self.av("NOT (idade = 3)", (1, "x", None)))

    def test_logica_de_tres_valores(self):
        n = (1, "x", None)
        self.assertFalse(self.av("idade = 3 AND 1 = 2", n))
        self.assertIsNone(self.av("idade = 3 AND 1 = 1", n))
        self.assertTrue(self.av("idade = 3 OR 1 = 1", n))
        self.assertIsNone(self.av("idade = 3 OR 1 = 2", n))

    def test_is_null_in_between_like(self):
        n = (1, "x", None)
        self.assertTrue(self.av("idade IS NULL", n))
        self.assertTrue(self.av("idade IS NOT NULL"))
        self.assertTrue(self.av("idade IN (1, 30)"))
        self.assertFalse(self.av("idade IN (1, 2)"))
        self.assertIsNone(self.av("idade IN (1, NULL)"))
        self.assertTrue(self.av("idade NOT IN (1, 2)"))
        self.assertIsNone(self.av("idade IN (1, 2)", n))
        self.assertTrue(self.av("idade BETWEEN 18 AND 30"))
        self.assertTrue(self.av("idade NOT BETWEEN 40 AND 50"))
        self.assertTrue(self.av("nome LIKE 'a_a'"))
        self.assertTrue(self.av("nome LIKE '%n%'"))
        self.assertFalse(self.av("nome LIKE 'b%'"))
        self.assertTrue(self.av("nome NOT LIKE 'b%'"))
        self.assertTrue(self.av("'a.c' LIKE 'a.c'"))
        self.assertFalse(self.av("'abc' LIKE 'a.c'"))  # ponto é literal

    def test_funcoes(self):
        self.assertEqual(self.av("UPPER(nome)"), "ANA")
        self.assertEqual(self.av("LENGTH(nome) + ABS(-2)"), 5)
        self.assertEqual(self.av("COALESCE(idade, 0)", (1, "x", None)), 0)
        self.assertEqual(self.av("nome + 'z'"), "anaz")
        with self.assertRaises(ErroExecucao):
            self.av("FOO(1)")

    def test_erros(self):
        with self.assertRaises(ErroExecucao):
            self.av("zzz")
        with self.assertRaises(ErroExecucao):
            self.av("nome = 1")
        with self.assertRaises(ErroExecucao):
            self.av("COUNT(idade)")
        with self.assertRaises(ErroExecucao):
            avaliar(expr("id"), [("a", "id"), ("b", "id")], (1, 2))  # ambígua
        self.assertEqual(avaliar(expr("b.id"), [("a", "id"), ("b", "id")], (1, 2)), 2)


class TestOperadores(unittest.TestCase):
    def test_scan_exige_abrir(self):
        with self.assertRaises(ErroExecucao):
            usuarios().proximo()

    def test_scan_e_filtro_descartam_unknown(self):
        f = Filtro(usuarios(), onde("idade >= 18"))
        self.assertEqual([l[0] for l in f], [1, 4])  # NULL e 17 saem

    def test_pode_reabrir(self):
        f = Filtro(usuarios(), onde("nome = 'ana'"))
        self.assertEqual(len(f.todas()), 2)
        self.assertEqual(len(f.todas()), 2)

    def test_projecao(self):
        p = Projecao(usuarios(), [(expr("nome"), "n"), (expr("idade * 2"), "dobro")])
        self.assertEqual(p.todas()[0], ("ana", 60))
        self.assertEqual(p.esquema, [("", "n"), ("", "dobro")])

    def test_juncao_loop_aninhado(self):
        j = JuncaoLoopAninhado(usuarios(), pedidos(), onde("u.id = p.uid"))
        self.assertEqual(sorted((l[0], l[3]) for l in j), [(1, 10), (1, 11), (3, 12)])

    def test_produto_cartesiano(self):
        self.assertEqual(len(JuncaoLoopAninhado(usuarios(), pedidos()).todas()), 16)

    def test_juncao_com_lado_vazio(self):
        vazio = Scan("v", ["a"], [])
        self.assertEqual(JuncaoLoopAninhado(usuarios(), vazio).todas(), [])
        self.assertEqual(JuncaoLoopAninhado(vazio, usuarios()).todas(), [])

    def test_limite_nao_consome_alem_do_necessario(self):
        s = usuarios()
        self.assertEqual(len(Limite(s, 2).todas()), 2)
        self.assertEqual(s.lidas, 2)
        self.assertEqual(Limite(usuarios(), 0).todas(), [])
        self.assertEqual([l[0] for l in Limite(usuarios(), 2, 1)], [2, 3])
        self.assertEqual(Limite(usuarios(), 5, 10).todas(), [])
        with self.assertRaises(ErroExecucao):
            Limite(usuarios(), -1)

    def test_distinto(self):
        p = Projecao(usuarios(), [(expr("nome"), "nome")])
        self.assertEqual(Distinto(p).todas(), [("ana",), ("bia",), ("caio",)])

    def test_ordenacao_multipla_estavel_com_nulls(self):
        o = Ordenacao(usuarios(), [(expr("nome"), False), (expr("idade"), True)])
        self.assertEqual([l[0] for l in o], [4, 1, 2, 3])
        o = Ordenacao(usuarios(), [(expr("idade"), False)])
        self.assertEqual([l[0] for l in o], [2, 3, 1, 4])  # NULL primeiro

    def test_pipeline_completo(self):
        plano = Limite(Ordenacao(Projecao(Filtro(
            JuncaoLoopAninhado(usuarios(), pedidos(), onde("u.id = p.uid")), onde("p.valor > 2")),
            [(expr("u.nome"), "nome"), (expr("p.valor"), "valor")]), [(expr("valor"), True)]), 1)
        self.assertEqual(plano.todas(), [("ana", 7.5)])


if __name__ == "__main__":
    unittest.main()
