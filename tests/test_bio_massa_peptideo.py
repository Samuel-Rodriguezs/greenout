import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bio_massa_peptideo import espectro_prefixos, massa, mz


class TestBioMassaPeptideo(unittest.TestCase):
    def test_alanina(self):
        self.assertAlmostEqual(massa("A"), 89.047675, places=5)

    def test_glicilglicina(self):
        self.assertAlmostEqual(massa("GG"), 132.053485, places=5)

    def test_isomeros(self):
        self.assertEqual(massa("IL"), massa("LI"))
        self.assertEqual(massa("ga"), massa("AG"))

    def test_mz(self):
        self.assertAlmostEqual(mz("A"), 90.054951, places=5)
        self.assertAlmostEqual(mz("A", 2), 45.5311135, places=5)
        with self.assertRaises(ValueError):
            mz("A", 0)

    def test_prefixos_rosalind(self):
        p = espectro_prefixos("SKADYEK")
        self.assertEqual(len(p), 7)
        self.assertAlmostEqual(p[0], 87.03203, places=5)
        self.assertAlmostEqual(p[-1], 821.39192, places=4)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            massa("")
        with self.assertRaises(ValueError):
            massa("AXB")
        with self.assertRaises(ValueError):
            espectro_prefixos("AB")


if __name__ == "__main__":
    unittest.main()
