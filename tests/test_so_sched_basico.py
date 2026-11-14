import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from so_sched_basico import Processo, fcfs, gantt, sjf, srtf

LIVRO = [
    Processo("P1", 0, 7),
    Processo("P2", 2, 4),
    Processo("P3", 4, 1),
    Processo("P4", 5, 4),
]


class TestSchedBasico(unittest.TestCase):
    def test_fcfs(self):
        r = fcfs(LIVRO)
        self.assertEqual(r.segmentos(), [("P1", 0, 7), ("P2", 7, 11), ("P3", 11, 12), ("P4", 12, 16)])
        self.assertEqual(r.espera, {"P1": 0, "P2": 5, "P3": 7, "P4": 7})
        self.assertAlmostEqual(r.espera_media, 4.75)
        self.assertAlmostEqual(r.retorno_medio, 8.75)

    def test_sjf_nao_preemptivo(self):
        r = sjf(LIVRO)
        self.assertEqual(r.segmentos(), [("P1", 0, 7), ("P3", 7, 8), ("P2", 8, 12), ("P4", 12, 16)])
        self.assertAlmostEqual(r.espera_media, 4.0)

    def test_srtf(self):
        r = srtf(LIVRO)
        self.assertEqual(
            r.segmentos(),
            [("P1", 0, 2), ("P2", 2, 4), ("P3", 4, 5), ("P2", 5, 7), ("P4", 7, 11), ("P1", 11, 16)],
        )
        self.assertEqual(r.conclusao, {"P1": 16, "P2": 7, "P3": 5, "P4": 11})
        self.assertAlmostEqual(r.espera_media, 3.0)
        self.assertAlmostEqual(r.retorno_medio, 7.0)

    def test_srtf_melhor_espera_que_fcfs(self):
        self.assertLess(srtf(LIVRO).espera_media, fcfs(LIVRO).espera_media)

    def test_ocioso_entre_processos(self):
        r = fcfs([Processo("A", 0, 2), Processo("B", 5, 1)])
        self.assertEqual(r.segmentos(), [("A", 0, 2), (None, 2, 5), ("B", 5, 6)])
        self.assertEqual(r.espera["B"], 0)

    def test_gantt_texto(self):
        r = fcfs([Processo("A", 0, 2), Processo("B", 0, 3)])
        self.assertEqual(gantt(r.linha_tempo), "| A | B |\n0   2   5")

    def test_validacao(self):
        with self.assertRaises(ValueError):
            fcfs([])
        with self.assertRaises(ValueError):
            fcfs([Processo("A", 0, 1), Processo("A", 1, 1)])
        with self.assertRaises(ValueError):
            fcfs([Processo("A", 0, 0)])


if __name__ == "__main__":
    unittest.main()
