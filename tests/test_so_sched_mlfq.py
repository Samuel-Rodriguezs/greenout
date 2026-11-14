import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from so_sched_basico import Processo
from so_sched_mlfq import mlfq


class TestMLFQ(unittest.TestCase):
    def test_democao_por_quantum(self):
        r, niveis = mlfq([Processo("A", 0, 7), Processo("B", 1, 3)])
        self.assertEqual(list("".join(p or "-" for p in r.linha_tempo)), list("AABBAAAABA"))
        self.assertEqual(r.conclusao, {"A": 10, "B": 9})
        self.assertEqual(r.espera, {"A": 3, "B": 5})
        self.assertEqual(niveis, (0, 0, 0, 0, 1, 1, 1, 1, 1, 2))

    def test_preempcao_por_chegada_em_nivel_superior(self):
        procs = [Processo("A", 0, 7), Processo("B", 1, 3), Processo("C", 5, 1)]
        r, _ = mlfq(procs)
        self.assertEqual("".join(r.linha_tempo), "AABBACBAAAA")
        self.assertEqual(r.conclusao, {"A": 11, "B": 7, "C": 6})

    def test_ultimo_nivel_gira(self):
        r, niveis = mlfq([Processo("A", 0, 20)], quanta=(1, 2, 4))
        self.assertEqual(niveis[:7], (0, 1, 1, 2, 2, 2, 2))
        self.assertEqual(set(niveis[7:]), {2})

    def test_reforco_devolve_ao_nivel_zero(self):
        _, niveis = mlfq([Processo("A", 0, 12)], quanta=(1, 2, 4), reforco=5)
        self.assertEqual(niveis[:11], (0, 1, 1, 2, 2, 0, 1, 1, 2, 2, 0))

    def test_ocioso(self):
        r, niveis = mlfq([Processo("A", 3, 1)])
        self.assertEqual(r.segmentos(), [(None, 0, 3), ("A", 3, 4)])
        self.assertEqual(niveis, (None, None, None, 0))

    def test_validacao(self):
        with self.assertRaises(ValueError):
            mlfq([Processo("A", 0, 1)], quanta=())
        with self.assertRaises(ValueError):
            mlfq([Processo("A", 0, 1)], reforco=0)


if __name__ == "__main__":
    unittest.main()
