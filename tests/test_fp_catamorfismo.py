import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fp_catamorfismo import (
    ConsF, Fix, NilF, alg_avaliar, alg_mostrar, alg_para_lista,
    alg_produto, alg_profundidade, ana, cata, coalg_intervalo, coalg_somas,
    desdobrar, dobrar_d, fatorial, hylo, mul, neg, num, soma,
)


class TestCatamorfismo(unittest.TestCase):
    def setUp(self):
        # -(2 + 3) * 4
        self.e = mul(neg(soma(num(2), num(3))), num(4))

    def test_cata_algebras(self):
        self.assertEqual(cata(alg_avaliar, self.e), -20)
        self.assertEqual(cata(alg_mostrar, self.e), "(-(2 + 3) * 4)")
        self.assertEqual(cata(alg_profundidade, self.e), 4)
        self.assertEqual(cata(alg_avaliar, num(7)), 7)

    def test_cata_com_fix_reconstroi(self):
        # cata(Fix) é a identidade (lei de reflexão)
        self.assertEqual(cata(Fix, self.e), self.e)

    def test_ana_e_inverso_de_cata_em_listas(self):
        lista = ana(coalg_intervalo, 5)
        self.assertEqual(cata(alg_para_lista, lista), [5, 4, 3, 2, 1])
        self.assertEqual(cata(alg_para_lista, ana(coalg_intervalo, 0)), [])
        self.assertEqual(lista.un, ConsF(5, ana(coalg_intervalo, 4)))

    def test_ana_arvore_de_somas(self):
        t = ana(coalg_somas, 6)
        self.assertEqual(cata(alg_avaliar, t), 6)
        self.assertEqual(cata(alg_profundidade, t), 4)
        self.assertEqual(cata(alg_avaliar, ana(coalg_somas, 1)), 1)

    def test_hilomorfismo_equivale_a_cata_apos_ana(self):
        for n in range(0, 12):
            self.assertEqual(
                hylo(alg_produto, coalg_intervalo, n),
                cata(alg_produto, ana(coalg_intervalo, n)),
            )
        for n in range(1, 20):
            self.assertEqual(hylo(alg_avaliar, coalg_somas, n), n)

    def test_fatorial(self):
        self.assertEqual([fatorial(n) for n in range(8)], [math.factorial(n) for n in range(8)])
        with self.assertRaises(ValueError):
            fatorial(-1)

    def test_dobrar_d_e_ordem(self):
        self.assertEqual(dobrar_d(lambda x, a: a + [x], [], [1, 2, 3]), [3, 2, 1])
        self.assertEqual(dobrar_d(lambda x, a: x - a, 0, [1, 2, 3]), 2)
        self.assertEqual(dobrar_d(lambda x, a: a, "z", []), "z")
        self.assertEqual(dobrar_d(lambda x, a: x + a, "", iter("abc")), "abc")

    def test_desdobrar(self):
        self.assertEqual(list(desdobrar(lambda n: (n, n - 1) if n > 0 else None, 4)), [4, 3, 2, 1])
        self.assertEqual(list(desdobrar(lambda n: None, 0)), [])
        collatz = lambda n: None if n == 0 else (n, 0 if n == 1 else (n // 2 if n % 2 == 0 else 3 * n + 1))
        self.assertEqual(list(desdobrar(collatz, 6)), [6, 3, 10, 5, 16, 8, 4, 2, 1])
        fibs = desdobrar(lambda p: (p[0], (p[1], p[0] + p[1])), (0, 1))
        self.assertEqual([next(fibs) for _ in range(8)], [0, 1, 1, 2, 3, 5, 8, 13])
        self.assertEqual(NilF().fmap(abs), NilF())


if __name__ == "__main__":
    unittest.main()
