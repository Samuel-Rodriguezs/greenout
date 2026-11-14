import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from so_sched_basico import Processo, fcfs
from so_sched_rr import round_robin, trocas_de_contexto


class TestRoundRobin(unittest.TestCase):
    def test_livro_silberschatz(self):
        procs = [Processo("P1", 0, 24), Processo("P2", 0, 3), Processo("P3", 0, 3)]
        r = round_robin(procs, 4)
        self.assertEqual(
            r.segmentos(),
            [("P1", 0, 4), ("P2", 4, 7), ("P3", 7, 10), ("P1", 10, 30)],
        )
        self.assertEqual(r.espera, {"P1": 6, "P2": 4, "P3": 7})
        self.assertAlmostEqual(r.espera_media, 17 / 3)

    def test_com_chegadas_escalonadas(self):
        procs = [
            Processo("P1", 0, 5),
            Processo("P2", 1, 3),
            Processo("P3", 2, 1),
            Processo("P4", 3, 2),
        ]
        r = round_robin(procs, 2)
        self.assertEqual(r.conclusao, {"P1": 11, "P2": 10, "P3": 5, "P4": 9})
        self.assertEqual(r.espera, {"P1": 6, "P2": 6, "P3": 2, "P4": 4})
        self.assertAlmostEqual(r.espera_media, 4.5)
        self.assertEqual(
            list(r.linha_tempo),
            ["P1", "P1", "P2", "P2", "P3", "P1", "P1", "P4", "P4", "P2", "P1"],
        )

    def test_quantum_grande_vira_fcfs(self):
        procs = [Processo("A", 0, 5), Processo("B", 1, 3), Processo("C", 2, 4)]
        self.assertEqual(round_robin(procs, 100).linha_tempo, fcfs(procs).linha_tempo)

    def test_quantum_1_alterna(self):
        r = round_robin([Processo("A", 0, 2), Processo("B", 0, 2)], 1)
        self.assertEqual(list(r.linha_tempo), ["A", "B", "A", "B"])
        self.assertEqual(trocas_de_contexto(r), 3)

    def test_cpu_ociosa(self):
        r = round_robin([Processo("A", 0, 1), Processo("B", 3, 1)], 2)
        self.assertEqual(r.segmentos(), [("A", 0, 1), (None, 1, 3), ("B", 3, 4)])

    def test_quantum_invalido(self):
        with self.assertRaises(ValueError):
            round_robin([Processo("A", 0, 1)], 0)


if __name__ == "__main__":
    unittest.main()
