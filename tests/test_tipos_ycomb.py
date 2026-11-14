import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from tipos_beta import normalizar, passo_normal
from tipos_termos import App, alfa_equivalentes, analisar, livres
from tipos_ycomb import (FAT_GERADOR, Y, Z, fatorial_church, y_python_estrito,
                         z_python)


class TestYZ(unittest.TestCase):
    def test_combinadores_fechados(self):
        self.assertEqual(livres(Y), frozenset())
        self.assertEqual(livres(Z), frozenset())
        self.assertEqual(livres(FAT_GERADOR), frozenset())

    def test_y_satisfaz_ponto_fixo(self):
        # Y f -> ... -> f (X), onde X reduz de volta para f X
        t = App(Y, analisar("f"))
        t = passo_normal(passo_normal(t))
        self.assertIsInstance(t, App)
        self.assertEqual(t.fun, analisar("f"))
        omega_f = t.arg
        self.assertTrue(alfa_equivalentes(
            passo_normal(omega_f), App(analisar("f"), omega_f)))

    def test_y_nao_tem_forma_normal_com_f_generico(self):
        t = App(Y, analisar("f"))
        for _ in range(30):
            t = passo_normal(t)
            self.assertIsNotNone(t)

    def test_y_com_funcao_constante_termina(self):
        # Y (\f.a) = a, pois a ordem normal descarta o argumento recursivo
        r = normalizar(App(Y, analisar("\\f.a")))
        self.assertEqual(r, analisar("a"))

    def test_fatorial_lambda(self):
        self.assertEqual(fatorial_church(0), 1)
        self.assertEqual(fatorial_church(1), 1)
        self.assertEqual(fatorial_church(3), 6)

    def test_fatorial_lambda_com_z(self):
        self.assertEqual(fatorial_church(3, Z), 6)

    def test_z_python_fatorial(self):
        fat = z_python(lambda f: lambda n: 1 if n == 0 else n * f(n - 1))
        self.assertEqual(fat(0), 1)
        self.assertEqual(fat(10), 3628800)

    def test_z_python_fibonacci(self):
        fib = z_python(lambda f: lambda n: n if n < 2 else f(n - 1) + f(n - 2))
        self.assertEqual([fib(i) for i in range(10)], [0, 1, 1, 2, 3, 5, 8, 13, 21, 34])

    def test_y_estrito_diverge(self):
        with self.assertRaises(RecursionError):
            y_python_estrito(lambda f: lambda n: n)


if __name__ == "__main__":
    unittest.main()
