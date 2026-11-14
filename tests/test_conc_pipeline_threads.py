import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from conc_pipeline_threads import PipelineThreads


class TestPipelineThreads(unittest.TestCase):
    def test_ordem_preservada(self):
        p = PipelineThreads([lambda x: x + 1, lambda x: x * 2, str])
        self.assertEqual(p.executar(range(100))[:3], ["2", "4", "6"])
        self.assertEqual(len(p.executar(range(100))), 100)

    def test_filtragem(self):
        p = PipelineThreads(
            [lambda x: x if x % 2 == 0 else PipelineThreads.DESCARTAR, lambda x: x * x]
        )
        self.assertEqual(p.executar(range(10)), [0, 4, 16, 36, 64])

    def test_estagios_em_threads_distintas(self):
        ids = []
        lock = threading.Lock()

        def marca(x):
            with lock:
                ids.append(threading.get_ident())
            return x

        PipelineThreads([marca, marca, marca]).executar([1])
        self.assertEqual(len(set(ids)), 3)

    def test_estagios_sobrepostos(self):
        # estágio 1 processa o item 1 enquanto o estágio 2 processa o item 0:
        # só se encontram na barreira se rodarem em paralelo
        b = threading.Barrier(2, timeout=2)

        def e1(x):
            if x == 1:
                b.wait()
            return x

        def e2(x):
            if x == 0:
                b.wait()
            return x

        p = PipelineThreads([e1, e2], capacidade=2)
        self.assertEqual(p.executar([0, 1]), [0, 1])

    def test_erro_propagado(self):
        p = PipelineThreads([lambda x: 10 // x])
        with self.assertRaises(ZeroDivisionError):
            p.executar([1, 0, 2])

    def test_entrada_vazia(self):
        self.assertEqual(PipelineThreads([str]).executar([]), [])

    def test_sem_estagios(self):
        with self.assertRaises(ValueError):
            PipelineThreads([])


if __name__ == "__main__":
    unittest.main()
