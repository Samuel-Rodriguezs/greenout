import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fp_composicao import (
    Fn, atributo, canalizar, compose, constante, contar_palavras_unicas,
    espiar, filtro, identidade, mapa, metodo, pipe, reduzir,
)

f = lambda x: x + 1
g = lambda x: x * 2
h = lambda x: x - 3


class TestComposicao(unittest.TestCase):
    def test_ordem(self):
        self.assertEqual(compose(f, g)(5), 11)  # f(g(5))
        self.assertEqual(pipe(f, g)(5), 12)  # g(f(5))
        self.assertEqual(canalizar(5, f, g, h), 9)

    def test_identidade_e_vazio(self):
        for x in (0, "a", None):
            self.assertEqual(compose()(x), x)
            self.assertEqual(pipe()(x), x)
            self.assertEqual(compose(identidade, f)(1), compose(f, identidade)(1))

    def test_associatividade(self):
        for x in range(-3, 4):
            self.assertEqual(compose(compose(f, g), h)(x), compose(f, compose(g, h))(x))
            self.assertEqual(pipe(pipe(f, g), h)(x), pipe(f, pipe(g, h))(x))

    def test_pipe_e_compose_sao_duais(self):
        self.assertEqual(pipe(f, g, h)(4), compose(h, g, f)(4))

    def test_fn_operadores(self):
        F, G = Fn(f), Fn(g)
        self.assertEqual((F >> G)(5), 12)
        self.assertEqual((F << G)(5), 11)
        self.assertEqual((F | g | h)(5), 9)
        self.assertEqual(5 >> (F >> G), 12)
        self.assertEqual(Fn(lambda a, b: a + b)(1, 2), 3)
        self.assertEqual((Fn(lambda a, b: a + b) >> g)(1, 2), 6)

    def test_colecoes_point_free(self):
        proc = pipe(filtro(lambda x: x % 2 == 0), mapa(lambda x: x * x), reduzir(lambda a, b: a + b, 0))
        self.assertEqual(proc(range(10)), 120)
        self.assertEqual(proc([]), 0)

    def test_espiar_e_constante(self):
        visto = []
        r = pipe(f, espiar(visto.append), g)(1)
        self.assertEqual((r, visto), (4, [2]))
        self.assertEqual(constante(7)(1, 2, x=3), 7)

    def test_atributo_metodo_exemplo(self):
        class P:
            nome = "ana"
        self.assertEqual(atributo("nome")(P()), "ana")
        self.assertEqual(metodo("replace", "a", "o")("banana"), "bonono")
        self.assertEqual(pipe(atributo("nome"), metodo("upper"))(P()), "ANA")
        self.assertEqual(contar_palavras_unicas("A a b B c"), 3)


if __name__ == "__main__":
    unittest.main()
