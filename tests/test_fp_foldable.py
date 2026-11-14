import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import fp_maybe
import fp_resultado
import fp_validacao
from fp_foldable import (
    ALGUM, LISTA, PRODUTO, SOMA, TODOS, VAZIA, Folha, No, altura, de_iteravel,
    dobrar_d, dobrar_e, elem, fmap, fold_map, para_lista, percorrer, sequence,
    tamanho, traverse,
)

MAYBE = (fp_maybe.unit, fp_maybe.lift2)


def lift2_resultado(f, a, b):
    return a.map(lambda x: lambda y: f(x, y)).ap(b)


RESULT = (fp_resultado.unit, lift2_resultado)


def lift2_valid(f, a, b):
    return fp_validacao.aplicar(f, a, b)


VALID = (fp_validacao.unit, lift2_valid)


class TestFoldable(unittest.TestCase):
    def test_ordem_e_construcao(self):
        t = de_iteravel(range(7))
        self.assertEqual(para_lista(t), list(range(7)))
        self.assertEqual(list(percorrer(t)), list(range(7)))
        self.assertEqual(altura(t), 3)
        self.assertEqual(de_iteravel([]), VAZIA)
        self.assertEqual(altura(VAZIA), 0)

    def test_dobras(self):
        t = de_iteravel([1, 2, 3, 4])
        self.assertEqual(dobrar_d(lambda x, a: x - a, 0, t), 1 - (2 - (3 - (4 - 0))))
        self.assertEqual(dobrar_e(lambda a, x: a - x, 0, t), ((((0 - 1) - 2) - 3) - 4))
        self.assertEqual(dobrar_e(lambda a, x: a + [x], [], t), [1, 2, 3, 4])

    def test_fold_map_monoides(self):
        t = de_iteravel([1, 2, 3, 4])
        self.assertEqual(fold_map(SOMA, lambda x: x, t), 10)
        self.assertEqual(fold_map(PRODUTO, lambda x: x, t), 24)
        self.assertEqual(fold_map(TODOS, lambda x: x > 0, t), True)
        self.assertEqual(fold_map(ALGUM, lambda x: x > 3, t), True)
        self.assertEqual(fold_map(LISTA, lambda x: (x, x), t), (1, 1, 2, 2, 3, 3, 4, 4))
        self.assertEqual(fold_map(SOMA, lambda x: x, VAZIA), 0)

    def test_tamanho_elem(self):
        t = de_iteravel("abcde")
        self.assertEqual(tamanho(t), 5)
        self.assertTrue(elem("c", t))
        self.assertFalse(elem("z", t))
        self.assertFalse(elem("a", VAZIA))

    def test_functor_leis(self):
        t = de_iteravel([1, 2, 3])
        self.assertEqual(fmap(lambda x: x, t), t)
        f, g = (lambda x: x + 1), (lambda x: x * 2)
        self.assertEqual(fmap(lambda x: g(f(x)), t), fmap(g, fmap(f, t)))

    def test_traverse_maybe(self):
        t = de_iteravel([2, 4, 6])
        par = lambda x: fp_maybe.Just(x // 2) if x % 2 == 0 else fp_maybe.NADA
        r = traverse(par, t, *MAYBE)
        self.assertEqual(r, fp_maybe.Just(de_iteravel([1, 2, 3])))
        r2 = traverse(par, de_iteravel([2, 3]), *MAYBE)
        self.assertEqual(r2, fp_maybe.NADA)

    def test_traverse_identidade_e_ordem(self):
        t = de_iteravel([1, 2, 3, 4, 5])
        self.assertEqual(traverse(fp_maybe.unit, t, *MAYBE), fp_maybe.unit(t))
        visitados = []
        def f(x):
            visitados.append(x)
            return fp_resultado.Ok(x)
        traverse(f, t, *RESULT)
        self.assertEqual(visitados, [1, 2, 3, 4, 5])
        self.assertEqual(traverse(fp_maybe.unit, VAZIA, *MAYBE), fp_maybe.unit(VAZIA))

    def test_traverse_validacao_acumula(self):
        t = de_iteravel([1, -2, 3, -4])
        v = lambda x: fp_validacao.Valido(x) if x > 0 else fp_validacao.erro(f"{x} <= 0")
        r = traverse(v, t, *VALID)
        self.assertEqual(r, fp_validacao.erro("-2 <= 0", "-4 <= 0"))

    def test_sequence(self):
        t = de_iteravel([fp_resultado.Ok(1), fp_resultado.Ok(2)])
        self.assertEqual(sequence(t, *RESULT), fp_resultado.Ok(de_iteravel([1, 2])))
        t2 = de_iteravel([fp_resultado.Ok(1), fp_resultado.Err("x")])
        self.assertEqual(sequence(t2, *RESULT), fp_resultado.Err("x"))
        self.assertIsInstance(Folha(), Folha)
        self.assertIsInstance(de_iteravel([1]), No)


if __name__ == "__main__":
    unittest.main()
