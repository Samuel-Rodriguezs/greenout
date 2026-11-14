import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bio_conservacao import contagens, frequencias, informacao, pwm

ALIN = ["ACG", "ACT", "ATG"]


class TestBioConservacao(unittest.TestCase):
    def test_contagens(self):
        c = contagens(ALIN)
        self.assertEqual(c["A"], [3, 0, 0])
        self.assertEqual(c["C"], [0, 2, 0])
        self.assertEqual(c["T"], [0, 1, 1])
        self.assertEqual(c["G"], [0, 0, 2])

    def test_frequencias_somam_um(self):
        f = frequencias(ALIN)
        for i in range(3):
            self.assertAlmostEqual(sum(f[b][i] for b in "ACGT"), 1.0)
        self.assertAlmostEqual(f["C"][1], 2 / 3)

    def test_informacao(self):
        i = informacao(ALIN)
        self.assertAlmostEqual(i[0], 2.0)
        self.assertAlmostEqual(i[1], 1.0817, places=3)
        self.assertAlmostEqual(i[1], i[2])

    def test_informacao_minima(self):
        self.assertAlmostEqual(informacao(["A", "C", "G", "T"])[0], 0.0)

    def test_pwm(self):
        m = pwm(ALIN)
        self.assertAlmostEqual(m["A"][0], 1.4854, places=3)  # log2(0,7/0,25)
        self.assertLess(m["C"][0], 0)

    def test_invalido(self):
        with self.assertRaises(ValueError):
            contagens([])
        with self.assertRaises(ValueError):
            contagens(["AC", "A"])


if __name__ == "__main__":
    unittest.main()
