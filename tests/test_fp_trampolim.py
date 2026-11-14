import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fp_trampolim import (
    Chamada, Pronto, chamar, eh_par, executar, fatorial, fibonacci, memoizar,
    retornar, soma_ate, trampolim,
)


class TestTrampolim(unittest.TestCase):
    def test_profundidade_alem_do_limite_da_pilha(self):
        self.assertEqual(soma_ate(100_000), 100_000 * 100_001 // 2)
        self.assertTrue(eh_par(1_000_000))
        self.assertFalse(eh_par(1_000_001))

    def test_recursao_normal_estouraria(self):
        def soma(n):
            return 0 if n == 0 else n + soma(n - 1)
        with self.assertRaises(RecursionError):
            soma(1_000_000)

    def test_bordas(self):
        self.assertEqual(soma_ate(0), 0)
        self.assertTrue(eh_par(0))
        self.assertFalse(eh_par(1))
        with self.assertRaises(ValueError):
            eh_par(-1)

    def test_fatorial(self):
        self.assertEqual(fatorial(0), 1)
        self.assertEqual(fatorial(1), 1)
        self.assertEqual(fatorial(10), 3628800)
        self.assertEqual(fatorial(3000), fatorial(2999) * 3000)
        with self.assertRaises(ValueError):
            fatorial(-1)

    def test_executar_primitivas(self):
        self.assertEqual(executar(retornar(3)), 3)
        self.assertEqual(executar(5), 5)  # valor comum passa direto
        c = chamar(lambda a, b: Pronto(a + b), 1, 2)
        self.assertIsInstance(c, Chamada)
        self.assertEqual(executar(c), 3)

    def test_decorador_preserva_nome(self):
        @trampolim
        def contagem(n):
            """doc"""
            return Pronto("fim") if n == 0 else Chamada(contagem.passo, (n - 1,))
        self.assertEqual(contagem.__name__, "contagem")
        self.assertEqual(contagem(50_000), "fim")


class TestMemoizacao(unittest.TestCase):
    def test_fibonacci_linear(self):
        fibonacci.limpar()
        self.assertEqual(fibonacci(80), 23416728348467685)
        self.assertEqual(fibonacci.erros, 81)
        antes = fibonacci.acertos
        fibonacci(80)
        self.assertEqual(fibonacci.acertos, antes + 1)
        self.assertEqual(fibonacci.erros, 81)
        self.assertEqual(len(fibonacci), 81)

    def test_fibonacci_erro_nao_cacheado(self):
        with self.assertRaises(ValueError):
            fibonacci(-1)
        self.assertEqual(fibonacci(0), 0)
        self.assertEqual(fibonacci(1), 1)

    def test_memoizar_generico(self):
        chamadas = []

        @memoizar
        def quad(x, y=0):
            chamadas.append(x)
            return x * x

        self.assertEqual(quad(3), 9)
        self.assertEqual(quad(3), 9)
        self.assertEqual(chamadas, [3])
        self.assertEqual(quad(4), 16)
        self.assertEqual((quad.acertos, quad.erros), (1, 2))
        self.assertEqual(quad.__name__, "quad")
        quad.limpar()
        self.assertEqual(len(quad), 0)
        quad(3)
        self.assertEqual(chamadas, [3, 4, 3])


if __name__ == "__main__":
    unittest.main()
