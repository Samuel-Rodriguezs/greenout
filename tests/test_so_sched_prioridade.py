import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from so_sched_basico import Processo
from so_sched_prioridade import prioridade

FLUXO = [
    Processo("L", 0, 2, prioridade=10),
    Processo("H1", 0, 3, prioridade=1),
    Processo("H2", 3, 3, prioridade=1),
    Processo("H3", 6, 3, prioridade=1),
]


class TestPrioridade(unittest.TestCase):
    def test_nao_preemptivo(self):
        procs = [
            Processo("P", 0, 4, prioridade=3),
            Processo("Q", 1, 2, prioridade=1),
            Processo("R", 1, 1, prioridade=2),
        ]
        r = prioridade(procs, preemptivo=False)
        self.assertEqual(r.segmentos(), [("P", 0, 4), ("Q", 4, 6), ("R", 6, 7)])

    def test_preemptivo(self):
        procs = [
            Processo("P", 0, 4, prioridade=3),
            Processo("Q", 1, 2, prioridade=1),
            Processo("R", 1, 1, prioridade=2),
        ]
        r = prioridade(procs)
        self.assertEqual(
            r.segmentos(), [("P", 0, 1), ("Q", 1, 3), ("R", 3, 4), ("P", 4, 7)]
        )

    def test_inanicao_sem_aging(self):
        r = prioridade(FLUXO)
        self.assertEqual(r.conclusao["L"], 11)  # L só roda no fim
        self.assertEqual(r.espera["L"], 9)

    def test_aging_evita_inanicao(self):
        r = prioridade(FLUXO, intervalo=2, passo=5)
        self.assertEqual(
            list(r.linha_tempo),
            ["H1", "H1", "H1", "H2", "L", "L", "H2", "H2", "H3", "H3", "H3"],
        )
        self.assertEqual(r.conclusao, {"H1": 3, "H2": 8, "L": 6, "H3": 11})
        self.assertAlmostEqual(r.espera_media, 2.0)

    def test_aging_nao_passa_de_zero(self):
        r = prioridade(
            [Processo("A", 0, 2, prioridade=0), Processo("B", 0, 2, prioridade=0)],
            intervalo=1,
            passo=50,
        )
        self.assertEqual(r.conclusao, {"A": 2, "B": 4})

    def test_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            prioridade(FLUXO, intervalo=0)
        with self.assertRaises(ValueError):
            prioridade(FLUXO, intervalo=2, passo=0)


if __name__ == "__main__":
    unittest.main()
