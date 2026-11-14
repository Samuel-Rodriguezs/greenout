import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from conc_trampolim import eh_par, fatorial, mdc, recursiva, saltar, soma_ate, trampolim


class TestTrampolim(unittest.TestCase):
    def test_profundidade_alem_do_limite(self):
        n = sys.getrecursionlimit() * 20
        self.assertEqual(soma_ate(n), n * (n + 1) // 2)

    def test_recursao_ingenua_estouraria(self):
        def ingenua(n):
            return 0 if n == 0 else n + ingenua(n - 1)

        with self.assertRaises(RecursionError):
            ingenua(sys.getrecursionlimit() * 2)

    def test_fatorial(self):
        self.assertEqual(fatorial(20), math.factorial(20))
        self.assertEqual(fatorial(0), 1)

    def test_recursao_mutua(self):
        self.assertTrue(eh_par(100_000))
        self.assertFalse(eh_par(100_001))

    def test_mdc(self):
        self.assertEqual(mdc(48, 18), 6)
        self.assertEqual(mdc(-12, 8), 4)

    def test_resultado_simples(self):
        self.assertEqual(trampolim(lambda x: x + 1, 1), 2)

    def test_decorador(self):
        @recursiva
        def contagem(n, acc=0):
            return acc if n == 0 else saltar(contagem.__wrapped__, n - 1, acc + 1)

        self.assertEqual(contagem(50_000, 0), 50_000)


if __name__ == "__main__":
    unittest.main()
