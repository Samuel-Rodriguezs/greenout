import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import math

from mat_monte_carlo import estimar_pi


class TestMonteCarlo(unittest.TestCase):
    def test_aproxima_pi(self):
        self.assertAlmostEqual(estimar_pi(200_000, 1), math.pi, delta=0.02)

    def test_reprodutivel(self):
        self.assertEqual(estimar_pi(1000, 5), estimar_pi(1000, 5))

    def test_uma_amostra(self):
        self.assertIn(estimar_pi(1, 3), (0.0, 4.0))

    def test_invalido(self):
        with self.assertRaises(ValueError):
            estimar_pi(0)


if __name__ == "__main__":
    unittest.main()
