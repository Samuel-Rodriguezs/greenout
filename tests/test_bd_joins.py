import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bd_joins import JuncaoHash, JuncaoMesclagem, LoopAninhado
from bd_sql_parser import Coluna, parse
from bd_volcano import ErroExecucao, Scan

A = [(1, "a"), (2, "b"), (2, "b2"), (3, "c"), (None, "nulo"), (7, "g")]
B = [(2, "x"), (2, "y"), (3, "z"), (None, "n"), (4, "w")]


def esq(linhas=A):
    return Scan("a", ["k", "v"], linhas)


def dir_(linhas=B):
    return Scan("b", ["k", "w"], linhas)


def cond():
    return parse("SELECT * FROM t WHERE a.k = b.k").where


def todas(op):
    return sorted(op.todas(), key=repr)


def hash_(tipo="inner", a=A, b=B):
    return JuncaoHash(esq(a), dir_(b), Coluna("k", "a"), Coluna("k", "b"), tipo)


def merge(tipo="inner", a=A, b=B):
    return JuncaoMesclagem(esq(a), dir_(b), Coluna("k", "a"), Coluna("k", "b"), tipo)


def loop(tipo="inner", a=A, b=B):
    return LoopAninhado(esq(a), dir_(b), cond(), tipo)


class TestJoins(unittest.TestCase):
    def test_inner_tres_algoritmos_concordam(self):
        esperado = sorted([(2, "b", 2, "x"), (2, "b", 2, "y"), (2, "b2", 2, "x"),
                           (2, "b2", 2, "y"), (3, "c", 3, "z")], key=repr)
        for f in (hash_, merge, loop):
            self.assertEqual(todas(f()), esperado, f.__name__)

    def test_left_outer(self):
        for f in (hash_, merge, loop):
            r = todas(f("left"))
            self.assertEqual(len(r), 8, f.__name__)
            self.assertIn((1, "a", None, None), r)
            self.assertIn((None, "nulo", None, None), r)  # NULL nunca casa
            self.assertIn((7, "g", None, None), r)

    def test_nulos_nao_casam_entre_si(self):
        for f in (hash_, merge, loop):
            r = f().todas()
            self.assertFalse(any(l[0] is None for l in r), f.__name__)

    def test_lados_vazios(self):
        for f in (hash_, merge, loop):
            self.assertEqual(f(a=[]).todas(), [])
            self.assertEqual(f(b=[]).todas(), [])
            self.assertEqual(len(f("left", b=[]).todas()), len(A))
            self.assertEqual(f("left", a=[]).todas(), [])

    def test_chaves_totalmente_repetidas(self):
        a = [(1, "a")] * 3
        b = [(1, "b")] * 4
        for f in (hash_, merge, loop):
            self.assertEqual(len(f(a=a, b=b).todas()), 12, f.__name__)

    def test_aleatorio_equivalencia(self):
        rnd = random.Random(1)
        for _ in range(30):
            a = [(rnd.choice([None, 1, 2, 3, 4, 5]), i) for i in range(rnd.randrange(0, 15))]
            b = [(rnd.choice([None, 1, 2, 3, 6]), i) for i in range(rnd.randrange(0, 15))]
            for tipo in ("inner", "left"):
                ref = todas(loop(tipo, a, b))
                self.assertEqual(todas(hash_(tipo, a, b)), ref)
                self.assertEqual(todas(merge(tipo, a, b)), ref)

    def test_hash_faz_menos_comparacoes_que_loop(self):
        a = [(i, i) for i in range(100)]
        b = [(i, i) for i in range(100)]
        h, l = hash_(a=a, b=b), loop(a=a, b=b)
        h.todas()
        l.todas()
        self.assertEqual(l.comparacoes, 10_000)
        self.assertEqual(h.comparacoes, 100)

    def test_tipo_invalido_e_coluna_inexistente(self):
        with self.assertRaises(ErroExecucao):
            hash_("full")
        with self.assertRaises(ErroExecucao):
            JuncaoHash(esq(), dir_(), Coluna("zzz"), Coluna("k", "b"))

    def test_reabrir_repete_resultado(self):
        j = hash_()
        self.assertEqual(todas(j), todas(j))


if __name__ == "__main__":
    unittest.main()
