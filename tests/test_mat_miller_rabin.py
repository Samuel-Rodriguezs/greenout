import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from mat_miller_rabin import eh_primo


class TestMillerRabin(unittest.TestCase):
    def test_pequenos(self):
        primos = [n for n in range(50) if eh_primo(n)]
        self.assertEqual(primos, [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47])

    def test_bordas(self):
        for n in (-5, 0, 1):
            self.assertFalse(eh_primo(n))

    def test_carmichael(self):
        for n in (561, 1105, 1729, 41041):
            self.assertFalse(eh_primo(n))

    def test_grandes(self):
        self.assertTrue(eh_primo(2 ** 61 - 1))
        self.assertTrue(eh_primo(1_000_000_007))
        self.assertFalse(eh_primo(2 ** 61 + 1))
        self.assertFalse(eh_primo(1_000_000_007 * 998_244_353))


if __name__ == "__main__":
    unittest.main()
