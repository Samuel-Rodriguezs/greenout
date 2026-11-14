import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ordenacao import bubble_sort, merge_sort, quick_sort


class TestOrdenacao(unittest.TestCase):
    CASOS = [[], [1], [3, 1, 2], [5, 5, 1, 0, -2, 9], [1, 2, 3, 4]]

    def test_todos(self):
        for f in (bubble_sort, merge_sort, quick_sort):
            for caso in self.CASOS:
                with self.subTest(f=f.__name__, caso=caso):
                    self.assertEqual(f(caso), sorted(caso))

    def test_nao_muta_entrada(self):
        original = [3, 1, 2]
        bubble_sort(original)
        self.assertEqual(original, [3, 1, 2])


if __name__ == "__main__":
    unittest.main()
