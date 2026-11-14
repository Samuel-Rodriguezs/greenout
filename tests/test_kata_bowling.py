import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_bowling import pontuar


class TestKataBowling(unittest.TestCase):
    def test_partida_zerada(self):
        self.assertEqual(pontuar([0] * 20), 0)

    def test_todos_um(self):
        self.assertEqual(pontuar([1] * 20), 20)

    def test_um_spare(self):
        self.assertEqual(pontuar([5, 5, 3] + [0] * 17), 16)

    def test_um_strike(self):
        self.assertEqual(pontuar([10, 3, 4] + [0] * 16), 24)

    def test_partida_perfeita(self):
        self.assertEqual(pontuar([10] * 12), 300)

    def test_todos_spares(self):
        self.assertEqual(pontuar([5] * 21), 150)

    def test_decimo_frame_spare(self):
        self.assertEqual(pontuar([0] * 18 + [7, 3, 8]), 18)

    def test_decimo_frame_strike(self):
        self.assertEqual(pontuar([0] * 18 + [10, 10, 10]), 30)

    def test_exemplo_classico(self):
        r = [10, 7, 3, 9, 0, 10, 0, 8, 8, 2, 0, 6, 10, 10, 10, 8, 1]
        self.assertEqual(pontuar(r), 167)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            pontuar([11] + [0] * 19)
        with self.assertRaises(ValueError):
            pontuar([6, 6] + [0] * 18)
        with self.assertRaises(ValueError):
            pontuar([1, 1])
        with self.assertRaises(ValueError):
            pontuar([0] * 18 + [10, 10])


if __name__ == "__main__":
    unittest.main()
