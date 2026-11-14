import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_easing import FUNCOES, Tween, in_out_quad, interpolar, out_bounce, out_quad


class TestEasing(unittest.TestCase):
    def test_extremos_de_todas_as_curvas(self):
        for nome, f in FUNCOES.items():
            self.assertAlmostEqual(f(0.0), 0.0, places=9, msg=nome)
            self.assertAlmostEqual(f(1.0), 1.0, places=9, msg=nome)

    def test_valores_conhecidos(self):
        self.assertAlmostEqual(FUNCOES["in_quad"](0.5), 0.25)
        self.assertAlmostEqual(out_quad(0.5), 0.75)
        self.assertAlmostEqual(in_out_quad(0.5), 0.5)
        self.assertAlmostEqual(FUNCOES["in_cubic"](0.5), 0.125)
        self.assertAlmostEqual(FUNCOES["in_out_sine"](0.5), 0.5)
        self.assertAlmostEqual(out_bounce(0.5), 0.765625)

    def test_monotonicas(self):
        for nome in ("linear", "in_quad", "out_quad", "in_out_cubic", "in_sine", "out_sine",
                     "in_circ", "out_circ", "in_expo", "out_expo"):
            f = FUNCOES[nome]
            vals = [f(i / 100) for i in range(101)]
            self.assertEqual(vals, sorted(vals), nome)

    def test_back_e_elastic_ultrapassam(self):
        self.assertLess(FUNCOES["in_back"](0.2), 0)
        self.assertGreater(FUNCOES["out_back"](0.8), 1)
        self.assertGreater(max(FUNCOES["out_elastic"](i / 100) for i in range(101)), 1)

    def test_interpolar_clamp_e_erro(self):
        self.assertEqual(interpolar(10, 20, 0.5), 15)
        self.assertEqual(interpolar(10, 20, 5), 20)
        self.assertEqual(interpolar(10, 20, -1, "in_quad"), 10)
        self.assertAlmostEqual(interpolar(0, 100, 0.5, "in_quad"), 25)
        with self.assertRaises(ValueError):
            interpolar(0, 1, 0.5, "nada")

    def test_tween(self):
        t = Tween(0, 10, 2.0, "linear")
        self.assertEqual(t.avancar(1.0), 5.0)
        self.assertFalse(t.terminou)
        self.assertEqual(t.avancar(5.0), 10.0)
        self.assertTrue(t.terminou)

    def test_tween_invalido(self):
        with self.assertRaises(ValueError):
            Tween(0, 1, 0)
        with self.assertRaises(ValueError):
            Tween(0, 1, 1, "x")


if __name__ == "__main__":
    unittest.main()
