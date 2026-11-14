import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_loop_passo_fixo import LoopPassoFixo, interpolar


class TestLoop(unittest.TestCase):
    def test_passos_e_alpha(self):
        l = LoopPassoFixo(passo=0.1)
        chamadas = []
        alpha = l.avancar(0.25, chamadas.append)
        self.assertEqual(chamadas, [0.1, 0.1])
        self.assertAlmostEqual(alpha, 0.5)
        self.assertEqual(l.passos_totais, 2)

    def test_acumula_entre_quadros(self):
        l = LoopPassoFixo(passo=0.1)
        n = []
        for _ in range(10):
            l.avancar(0.03, n.append)
        self.assertEqual(len(n), 3)
        self.assertAlmostEqual(l.tempo_simulado, 0.3)

    def test_espiral_da_morte_limitada(self):
        l = LoopPassoFixo(passo=0.1, max_passos=3)
        n = []
        alpha = l.avancar(10.0, n.append)
        self.assertEqual(len(n), 3)
        self.assertTrue(0 <= alpha < 1)

    def test_deterministico(self):
        def roda():
            l = LoopPassoFixo(passo=1 / 60)
            pos = [0.0]
            for dt in (0.016, 0.017, 0.033, 0.001, 0.05):
                l.avancar(dt, lambda p: pos.__setitem__(0, pos[0] + 2 * p))
            return pos[0], l.passos_totais
        self.assertEqual(roda(), roda())

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            LoopPassoFixo(passo=0)
        with self.assertRaises(ValueError):
            LoopPassoFixo(max_passos=0)
        with self.assertRaises(ValueError):
            LoopPassoFixo().avancar(-1, lambda p: None)

    def test_interpolar(self):
        self.assertEqual(interpolar(10, 20, 0.25), 12.5)


if __name__ == "__main__":
    unittest.main()
