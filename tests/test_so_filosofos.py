import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from so_filosofos import simular


def inicios(r):
    return {fil: ini for ini, _, fil in r.intervalos}


class TestFilosofos(unittest.TestCase):
    def test_ingenuo_entra_em_deadlock(self):
        r = simular(5, "ingenuo")
        self.assertEqual(r.estado, "deadlock")
        self.assertEqual(r.bloqueados, [0, 1, 2, 3, 4])
        self.assertEqual(r.refeicoes, [0] * 5)
        self.assertEqual(r.fim, 2)

    def test_hierarquia_quebra_a_espera_circular(self):
        r = simular(5, "hierarquia")
        self.assertEqual(r.estado, "fim")
        self.assertEqual(r.refeicoes, [1] * 5)
        self.assertEqual(inicios(r), {3: 2, 2: 4, 1: 6, 0: 8, 4: 11})
        self.assertEqual(r.fim, 13)

    def test_garcom_tambem_evita_deadlock(self):
        r = simular(5, "garcom")
        self.assertEqual(r.estado, "fim")
        self.assertEqual(inicios(r), {3: 2, 2: 4, 1: 6, 0: 8, 4: 10})
        self.assertEqual(r.fim, 12)

    def test_vizinhos_nunca_comem_juntos(self):
        for estrategia in ("hierarquia", "garcom"):
            r = simular(5, estrategia, refeicoes=4, t_pensar=1, t_comer=3)
            self.assertEqual(r.estado, "fim")
            self.assertEqual(r.refeicoes, [4] * 5)
            for a in r.intervalos:
                for b in r.intervalos:
                    if a is b or (a[2] - b[2]) % 5 not in (1, 4):
                        continue
                    self.assertTrue(a[1] <= b[0] or b[1] <= a[0], (estrategia, a, b))

    def test_dois_filosofos_ingenuo_tambem_trava(self):
        r = simular(2, "ingenuo")
        self.assertEqual(r.estado, "deadlock")

    def test_validacao(self):
        with self.assertRaises(ValueError):
            simular(1, "garcom")
        with self.assertRaises(ValueError):
            simular(5, "random")
        with self.assertRaises(ValueError):
            simular(5, "garcom", t_comer=0)


if __name__ == "__main__":
    unittest.main()
