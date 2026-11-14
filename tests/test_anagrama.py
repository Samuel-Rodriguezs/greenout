import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from anagrama import sao_anagramas


class TestAnagrama(unittest.TestCase):
    def test_positivo(self):
        self.assertTrue(sao_anagramas("Amor", "Roma"))

    def test_negativo(self):
        self.assertFalse(sao_anagramas("casa", "caso"))


if __name__ == "__main__":
    unittest.main()
