import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from alg_hanoi import hanoi


class TesteHanoi(unittest.TestCase):
    def test_zero_discos(self):
        self.assertEqual(hanoi(0), [])

    def test_um_disco(self):
        self.assertEqual(hanoi(1), [("A", "C")])

    def test_tres_discos(self):
        self.assertEqual(
            hanoi(3),
            [("A", "C"), ("A", "B"), ("C", "B"), ("A", "C"), ("B", "A"), ("B", "C"), ("A", "C")],
        )

    def test_quantidade_minima(self):
        for n in range(0, 10):
            self.assertEqual(len(hanoi(n)), 2**n - 1)

    def test_simulacao_valida(self):
        n = 5
        pinos = {"A": list(range(n, 0, -1)), "B": [], "C": []}
        for de, para in hanoi(n):
            disco = pinos[de].pop()
            if pinos[para]:
                self.assertGreater(pinos[para][-1], disco)
            pinos[para].append(disco)
        self.assertEqual(pinos["C"], list(range(n, 0, -1)))

    def test_nomes_personalizados(self):
        self.assertEqual(hanoi(1, "x", "y", "z"), [("x", "z")])

    def test_negativo(self):
        with self.assertRaises(ValueError):
            hanoi(-1)


if __name__ == "__main__":
    unittest.main()
