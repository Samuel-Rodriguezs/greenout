import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from primos import eh_primo, primos_ate


class TestPrimos(unittest.TestCase):
    def test_eh_primo(self):
        self.assertTrue(eh_primo(97))
        self.assertFalse(eh_primo(1))
        self.assertFalse(eh_primo(91))

    def test_crivo(self):
        self.assertEqual(primos_ate(30), [2, 3, 5, 7, 11, 13, 17, 19, 23, 29])
        self.assertEqual(primos_ate(1), [])


if __name__ == "__main__":
    unittest.main()
