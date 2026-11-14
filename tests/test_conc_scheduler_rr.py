import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from conc_scheduler_rr import SchedulerRR


def contador(n, nome, log):
    for i in range(n):
        log.append(f"{nome}{i}")
        yield
    return nome


class TestSchedulerRR(unittest.TestCase):
    def test_round_robin_quantum_1(self):
        log = []
        s = SchedulerRR(1)
        s.criar(contador(2, "a", log))
        s.criar(contador(2, "b", log))
        s.executar()
        self.assertEqual(log, ["a0", "b0", "a1", "b1"])

    def test_quantum_maior(self):
        log = []
        s = SchedulerRR(2)
        s.criar(contador(4, "a", log))
        s.criar(contador(4, "b", log))
        s.executar()
        self.assertEqual(log, ["a0", "a1", "b0", "b1", "a2", "a3", "b2", "b3"])

    def test_ordem_das_fatias(self):
        s = SchedulerRR(1)
        a = s.criar(contador(1, "a", []))
        b = s.criar(contador(3, "b", []))
        s.executar()
        # a termina na 2ª fatia (yield + StopIteration); b continua
        self.assertEqual(s.ordem_execucao[:4], [a, b, a, b])

    def test_resultado_e_terminado(self):
        s = SchedulerRR(3)
        pid = s.criar(contador(2, "x", []))
        s.executar()
        p = s.processos[pid]
        self.assertTrue(p.terminado)
        self.assertEqual(p.resultado, "x")
        self.assertEqual(p.passos, 2)

    def test_passo_a_passo(self):
        s = SchedulerRR(1)
        s.criar(contador(1, "a", []))
        self.assertTrue(s.passo())
        self.assertTrue(s.passo())
        self.assertFalse(s.passo())

    def test_justica_quanta(self):
        s = SchedulerRR(1)
        for i in range(3):
            s.criar(contador(5, str(i), []))
        s.executar()
        usos = [p.quanta_usados for p in s]
        self.assertEqual(usos, [6, 6, 6])

    def test_limite_fatias_e_quantum_invalido(self):
        def infinito():
            while True:
                yield

        s = SchedulerRR(1)
        s.criar(infinito())
        self.assertEqual(s.executar(max_fatias=10), 10)
        with self.assertRaises(ValueError):
            SchedulerRR(0)


if __name__ == "__main__":
    unittest.main()
