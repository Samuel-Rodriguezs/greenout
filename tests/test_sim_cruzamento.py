import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sim_cruzamento import Cruzamento, Fases


class TestCruzamento(unittest.TestCase):
    def test_ciclo(self):
        c = Cruzamento(Fases(2, 1, 1), rng=random.Random(1))
        self.assertEqual(c.duracao_ciclo, 8)
        seq = [c.estado(t) for t in range(8)]
        self.assertEqual(seq[0], {"NS": "verde", "LO": "vermelho"})
        self.assertEqual(seq[2], {"NS": "amarelo", "LO": "vermelho"})
        self.assertEqual(seq[3], {"NS": "vermelho", "LO": "vermelho"})
        self.assertEqual(seq[4], {"NS": "vermelho", "LO": "verde"})
        self.assertEqual(c.estado(8), seq[0])

    def test_nunca_dois_abertos(self):
        c = Cruzamento(rng=random.Random(1))
        for t in range(c.duracao_ciclo * 3):
            est = c.estado(t)
            abertos = [v for v, cor in est.items() if cor != "vermelho"]
            self.assertLessEqual(len(abertos), 1)

    def test_vazao_apenas_no_verde(self):
        c = Cruzamento(Fases(3, 1, 1), prob_chegada=1.0, rng=random.Random(1))
        c.executar(10)
        self.assertEqual(c.passaram, {"NS": 3, "LO": 3})
        self.assertEqual(c.filas["NS"], 10 - 3)

    def test_determinismo(self):
        a = Cruzamento(prob_chegada=0.4, rng=random.Random(7))
        b = Cruzamento(prob_chegada=0.4, rng=random.Random(7))
        a.executar(200)
        b.executar(200)
        self.assertEqual((a.filas, a.passaram), (b.filas, b.passaram))

    def test_sem_trafego(self):
        c = Cruzamento(prob_chegada=0.0, rng=random.Random(1))
        c.executar(50)
        self.assertEqual(c.passaram, {"NS": 0, "LO": 0})


if __name__ == "__main__":
    unittest.main()
