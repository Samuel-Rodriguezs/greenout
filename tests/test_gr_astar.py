import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_astar import astar


class TestAstar(unittest.TestCase):
    def test_reta(self):
        c = astar(["...."], (0, 0), (0, 3))
        self.assertEqual(c, [(0, 0), (0, 1), (0, 2), (0, 3)])

    def test_contorna_parede(self):
        grade = ["..#.", "..#.", "...."]
        c = astar(grade, (0, 0), (0, 3))
        self.assertEqual(len(c) - 1, 7)
        self.assertEqual(c[0], (0, 0))
        self.assertEqual(c[-1], (0, 3))
        for p in c:
            self.assertNotEqual(grade[p[0]][p[1]], "#")

    def test_sem_caminho(self):
        self.assertIsNone(astar([".#.", ".#."], (0, 0), (0, 2)))

    def test_inicio_igual_fim(self):
        self.assertEqual(astar(["."], (0, 0), (0, 0)), [(0, 0)])

    def test_extremos_invalidos(self):
        self.assertIsNone(astar(["#."], (0, 0), (0, 1)))
        self.assertIsNone(astar(["..."], (0, 0), (5, 5)))
        self.assertIsNone(astar([], (0, 0), (0, 0)))


if __name__ == "__main__":
    unittest.main()
