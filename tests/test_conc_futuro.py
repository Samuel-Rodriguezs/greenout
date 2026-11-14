import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from conc_futuro import Futuro, executar, todos


class TestFuturo(unittest.TestCase):
    def test_resolver_e_resultado(self):
        f = Futuro()
        self.assertFalse(f.pronto())
        f.resolver(42)
        self.assertEqual(f.resultado(), 42)
        self.assertEqual(f.estado, "resolvido")

    def test_rejeitar(self):
        f = Futuro()
        f.rejeitar(ValueError("x"))
        with self.assertRaises(ValueError):
            f.resultado()

    def test_dupla_conclusao(self):
        f = Futuro()
        f.resolver(1)
        with self.assertRaises(RuntimeError):
            f.resolver(2)

    def test_timeout(self):
        with self.assertRaises(TimeoutError):
            Futuro().resultado(0.01)

    def test_encadeamento(self):
        f = Futuro()
        g = f.entao(lambda x: x + 1).entao(lambda x: x * 10)
        f.resolver(1)
        self.assertEqual(g.resultado(1), 20)

    def test_callback_apos_conclusao(self):
        f = Futuro()
        f.resolver(5)
        vistos = []
        f.ao_concluir(lambda fut: vistos.append(fut.resultado()))
        self.assertEqual(vistos, [5])

    def test_erro_propaga_e_recupera(self):
        f = Futuro()
        g = f.entao(lambda x: x + 1).recuperar(lambda e: -1)
        f.rejeitar(RuntimeError("falha"))
        self.assertEqual(g.resultado(1), -1)

    def test_excecao_em_entao(self):
        f = Futuro()
        g = f.entao(lambda x: 1 / x)
        f.resolver(0)
        with self.assertRaises(ZeroDivisionError):
            g.resultado(1)

    def test_executar_em_thread(self):
        pronto = threading.Event()
        f = executar(lambda: pronto.wait(2) and "ok")
        self.assertFalse(f.pronto())
        pronto.set()
        self.assertEqual(f.resultado(2), "ok")

    def test_todos(self):
        a, b = Futuro(), Futuro()
        t = todos([a, b])
        b.resolver("b")
        self.assertFalse(t.pronto())
        a.resolver("a")
        self.assertEqual(t.resultado(1), ["a", "b"])

    def test_todos_rejeita_no_primeiro_erro(self):
        a, b = Futuro(), Futuro()
        t = todos([a, b])
        a.rejeitar(KeyError("k"))
        with self.assertRaises(KeyError):
            t.resultado(1)

    def test_todos_vazio(self):
        self.assertEqual(todos([]).resultado(1), [])


if __name__ == "__main__":
    unittest.main()
