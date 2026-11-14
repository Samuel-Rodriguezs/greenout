import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sim_rpg_dados import Expressao, intervalo, media, parse, rolar


class TestRpgDados(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(parse("2d6+3"), Expressao(2, 6, None, 0, 3))
        self.assertEqual(parse("d20"), Expressao(1, 20, None, 0, 0))
        self.assertEqual(parse(" 1D8 - 2 "), Expressao(1, 8, None, 0, -2))
        self.assertEqual(parse("4d6kh3"), Expressao(4, 6, "kh", 3, 0))
        self.assertEqual(parse("2d20kl1+5"), Expressao(2, 20, "kl", 1, 5))

    def test_parse_invalido(self):
        for t in ("", "abc", "2d", "0d6", "2d1", "4d6kh5", "2d6+", "2d6*3", "3x6"):
            with self.assertRaises(ValueError, msg=t):
                parse(t)

    def test_rolar_dentro_do_intervalo(self):
        rng = random.Random(1)
        lo, hi = intervalo("2d6+3")
        self.assertEqual((lo, hi), (5, 15))
        for _ in range(200):
            r = rolar("2d6+3", rng)
            self.assertTrue(lo <= r.total <= hi)
            self.assertEqual(r.total, sum(r.dados) + 3)

    def test_determinismo(self):
        self.assertEqual(rolar("3d8", random.Random(9)), rolar("3d8", random.Random(9)))

    def test_keep_highest_e_lowest(self):
        r = rolar("4d6kh3", random.Random(2))
        self.assertEqual(len(r.mantidos), 3)
        self.assertEqual(sorted(r.dados)[1:], sorted(r.mantidos))
        v = rolar("2d20kl1", random.Random(2))
        self.assertEqual(v.total, min(v.dados))

    def test_modificador_negativo(self):
        r = rolar("1d4-10", random.Random(3))
        self.assertEqual(r.total, r.dados[0] - 10)
        self.assertEqual(intervalo("1d4-10"), (-9, -6))

    def test_media_empirica_e_teorica(self):
        self.assertEqual(media("2d6+3"), 10.0)
        rng = random.Random(4)
        emp = sum(rolar("2d6+3", rng).total for _ in range(5000)) / 5000
        self.assertAlmostEqual(emp, 10.0, delta=0.2)
        with self.assertRaises(ValueError):
            media("4d6kh3")


if __name__ == "__main__":
    unittest.main()
