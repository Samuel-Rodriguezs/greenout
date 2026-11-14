import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fp_church import (
    anexar, cabeca, cons, de_bool, de_int, de_lista, dobrar, e_, eh_zero,
    exp_n, falso, filtro, mapa, mul_n, nao, nil, ou_, para_bool, para_int,
    para_lista, pred, reverter, soma, soma_n, sub_n, suc, tamanho, vazia,
    verdadeiro, zero,
)


class TestChurchListas(unittest.TestCase):
    def test_roundtrip(self):
        for xs in ([], [1], [1, 2, 3], list("abc")):
            self.assertEqual(para_lista(de_lista(xs)), xs)
        self.assertEqual(para_lista(cons(1, cons(2, nil))), [1, 2])

    def test_tamanho_vazia_cabeca(self):
        self.assertEqual(tamanho(de_lista([4, 5, 6])), 3)
        self.assertEqual(tamanho(nil), 0)
        self.assertTrue(vazia(nil))
        self.assertFalse(vazia(de_lista([0])))
        self.assertEqual(cabeca(de_lista([9, 8])), 9)
        self.assertEqual(cabeca(de_lista([None])), None)
        with self.assertRaises(IndexError):
            cabeca(nil)

    def test_mapa_filtro_soma(self):
        l = de_lista([1, 2, 3, 4])
        self.assertEqual(para_lista(mapa(lambda x: x * x, l)), [1, 4, 9, 16])
        self.assertEqual(para_lista(filtro(lambda x: x % 2 == 0, l)), [2, 4])
        self.assertEqual(soma(l), 10)
        self.assertEqual(dobrar(lambda h, acc: acc + [h], [], l), [4, 3, 2, 1])
        self.assertEqual(para_lista(mapa(abs, nil)), [])

    def test_leis_functor(self):
        l = de_lista([1, 2, 3])
        f, g = (lambda x: x + 1), (lambda x: x * 3)
        self.assertEqual(para_lista(mapa(lambda x: x, l)), [1, 2, 3])
        self.assertEqual(para_lista(mapa(lambda x: g(f(x)), l)), para_lista(mapa(g, mapa(f, l))))

    def test_anexar_reverter(self):
        a, b = de_lista([1, 2]), de_lista([3])
        self.assertEqual(para_lista(anexar(a, b)), [1, 2, 3])
        self.assertEqual(para_lista(anexar(nil, b)), [3])
        self.assertEqual(para_lista(anexar(a, nil)), [1, 2])
        self.assertEqual(para_lista(reverter(de_lista([1, 2, 3]))), [3, 2, 1])
        self.assertEqual(para_lista(reverter(nil)), [])
        c = de_lista([5])
        self.assertEqual(
            para_lista(anexar(anexar(a, b), c)), para_lista(anexar(a, anexar(b, c)))
        )


class TestChurchBooleanos(unittest.TestCase):
    def test_tabelas(self):
        for p in (True, False):
            self.assertEqual(para_bool(nao(de_bool(p))), not p)
            for q in (True, False):
                self.assertEqual(para_bool(e_(de_bool(p), de_bool(q))), p and q)
                self.assertEqual(para_bool(ou_(de_bool(p), de_bool(q))), p or q)

    def test_selecao(self):
        self.assertEqual(verdadeiro("a", "b"), "a")
        self.assertEqual(falso("a", "b"), "b")


class TestChurchNumerais(unittest.TestCase):
    def test_roundtrip_e_zero(self):
        for k in (0, 1, 5, 20):
            self.assertEqual(para_int(de_int(k)), k)
        self.assertEqual(para_int(zero), 0)
        self.assertEqual(para_int(suc(suc(zero))), 2)
        with self.assertRaises(ValueError):
            de_int(-1)

    def test_aritmetica(self):
        for a in range(5):
            for b in range(5):
                self.assertEqual(para_int(soma_n(de_int(a), de_int(b))), a + b)
                self.assertEqual(para_int(mul_n(de_int(a), de_int(b))), a * b)
                self.assertEqual(para_int(exp_n(de_int(a), de_int(b))), a ** b)
                self.assertEqual(para_int(sub_n(de_int(a), de_int(b))), max(a - b, 0))

    def test_eh_zero_e_pred(self):
        self.assertTrue(para_bool(eh_zero(zero)))
        self.assertFalse(para_bool(eh_zero(de_int(3))))
        self.assertEqual(para_int(pred(de_int(4))), 3)
        self.assertEqual(para_int(pred(zero)), 0)

    def test_aplicacao_generica(self):
        tres = de_int(3)
        self.assertEqual(tres(lambda s: s + "!", "x"), "x!!!")
        self.assertEqual(tres(lambda xs: [0] + xs, []), [0, 0, 0])


if __name__ == "__main__":
    unittest.main()
