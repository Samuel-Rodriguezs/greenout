import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_yahtzee import pontuar


class TestKataYahtzee(unittest.TestCase):
    def test_chance(self):
        self.assertEqual(pontuar([2, 3, 4, 5, 1], "chance"), 15)
        self.assertEqual(pontuar([3, 3, 4, 5, 1], "chance"), 16)

    def test_yahtzee(self):
        self.assertEqual(pontuar([4, 4, 4, 4, 4], "yahtzee"), 50)
        self.assertEqual(pontuar([6, 6, 6, 6, 3], "yahtzee"), 0)

    def test_numeros(self):
        self.assertEqual(pontuar([1, 1, 2, 4, 4], "uns"), 2)
        self.assertEqual(pontuar([2, 3, 2, 5, 1], "dois"), 4)
        self.assertEqual(pontuar([3, 3, 3, 4, 5], "tres"), 9)
        self.assertEqual(pontuar([1, 1, 2, 4, 4], "quatros"), 8)
        self.assertEqual(pontuar([5, 5, 5, 5, 5], "cincos"), 25)
        self.assertEqual(pontuar([1, 2, 3, 4, 5], "seis"), 0)

    def test_par(self):
        self.assertEqual(pontuar([3, 4, 3, 5, 6], "par"), 6)
        self.assertEqual(pontuar([5, 3, 3, 3, 5], "par"), 10)
        self.assertEqual(pontuar([1, 2, 3, 4, 6], "par"), 0)

    def test_dois_pares(self):
        self.assertEqual(pontuar([3, 3, 5, 4, 5], "dois_pares"), 16)
        self.assertEqual(pontuar([3, 3, 5, 5, 5], "dois_pares"), 16)
        self.assertEqual(pontuar([3, 3, 5, 4, 6], "dois_pares"), 0)

    def test_trinca_e_quadra(self):
        self.assertEqual(pontuar([3, 3, 3, 4, 5], "trinca"), 9)
        self.assertEqual(pontuar([3, 3, 4, 5, 5], "trinca"), 0)
        self.assertEqual(pontuar([3, 3, 3, 3, 5], "quadra"), 12)
        self.assertEqual(pontuar([3, 3, 3, 5, 5], "quadra"), 0)

    def test_sequencias(self):
        self.assertEqual(pontuar([3, 4, 5, 1, 2], "sequencia_pequena"), 15)
        self.assertEqual(pontuar([1, 2, 2, 4, 5], "sequencia_pequena"), 0)
        self.assertEqual(pontuar([6, 2, 3, 4, 5], "sequencia_grande"), 20)
        self.assertEqual(pontuar([1, 2, 3, 4, 5], "sequencia_grande"), 0)

    def test_full_house(self):
        self.assertEqual(pontuar([6, 2, 2, 2, 6], "full_house"), 18)
        self.assertEqual(pontuar([2, 3, 4, 5, 6], "full_house"), 0)
        self.assertEqual(pontuar([4, 4, 4, 4, 4], "full_house"), 0)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            pontuar([1, 2, 3], "chance")
        with self.assertRaises(ValueError):
            pontuar([1, 2, 3, 4, 7], "chance")
        with self.assertRaises(ValueError):
            pontuar([1, 2, 3, 4, 5], "outra")


if __name__ == "__main__":
    unittest.main()
