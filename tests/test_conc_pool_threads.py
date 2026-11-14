import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from conc_pool_threads import PoolThreads


class TestPoolThreads(unittest.TestCase):
    def test_mapear_preserva_ordem(self):
        with PoolThreads(3) as p:
            self.assertEqual(p.mapear(lambda x: x * x, [1, 2, 3, 4]), [1, 4, 9, 16])

    def test_excecao_propagada(self):
        with PoolThreads(1) as p:
            f = p.submeter(lambda: 1 / 0)
            with self.assertRaises(ZeroDivisionError):
                f.resultado(2)

    def test_execucao_concorrente(self):
        # duas tarefas só terminam se rodarem ao mesmo tempo (barreira)
        barreira = threading.Barrier(2, timeout=2)
        with PoolThreads(2) as p:
            fs = [p.submeter(barreira.wait) for _ in range(2)]
            for f in fs:
                f.resultado(2)
            self.assertTrue(all(f.pronto() for f in fs))

    def test_submeter_apos_encerrar(self):
        p = PoolThreads(1)
        p.encerrar()
        with self.assertRaises(RuntimeError):
            p.submeter(lambda: 1)

    def test_timeout_resultado(self):
        liberar = threading.Event()
        with PoolThreads(1) as p:
            f = p.submeter(liberar.wait, 2)
            with self.assertRaises(TimeoutError):
                f.resultado(0.01)
            liberar.set()
            self.assertTrue(f.resultado(2))

    def test_n_invalido(self):
        with self.assertRaises(ValueError):
            PoolThreads(0)


if __name__ == "__main__":
    unittest.main()
