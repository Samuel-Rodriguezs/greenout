import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from mdc_mmc import mdc, mmc


class TestMdcMmc(unittest.TestCase):
    def test_mdc_basico(self):
        self.assertEqual(mdc(12, 18), 6)

    def test_mdc_com_zero(self):
        self.assertEqual(mdc(0, 5), 5)
        self.assertEqual(mdc(7, 0), 7)
        self.assertEqual(mdc(0, 0), 0)

    def test_mdc_negativos(self):
        self.assertEqual(mdc(-12, 18), 6)

    def test_mdc_primos_entre_si(self):
        self.assertEqual(mdc(13, 8), 1)

    def test_mmc_basico(self):
        self.assertEqual(mmc(4, 6), 12)

    def test_mmc_com_zero(self):
        self.assertEqual(mmc(0, 5), 0)

    def test_mmc_negativos_e_iguais(self):
        self.assertEqual(mmc(-4, 6), 12)
        self.assertEqual(mmc(7, 7), 7)


if __name__ == "__main__":
    unittest.main()
