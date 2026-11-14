import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sim_batalha_naval import BatalhaNaval


class TestBatalhaNaval(unittest.TestCase):
    def test_posicionamento_sem_sobreposicao(self):
        b = BatalhaNaval(rng=random.Random(1))
        todas = [p for n in b.navios for p in n]
        self.assertEqual(len(todas), len(set(todas)))
        self.assertEqual(len(todas), 5 + 4 + 3 + 3 + 2)
        self.assertTrue(all(0 <= l < 10 and 0 <= c < 10 for l, c in todas))

    def test_determinismo(self):
        a = BatalhaNaval(rng=random.Random(7)).navios
        b = BatalhaNaval(rng=random.Random(7)).navios
        self.assertEqual(a, b)

    def test_tiros_e_vitoria(self):
        b = BatalhaNaval(6, (2, 3), random.Random(2))
        resultados = []
        for navio in b.navios:
            for p in sorted(navio):
                resultados.append(b.atirar(p))
        self.assertEqual(resultados.count("afundou"), 2)
        self.assertTrue(b.venceu)

    def test_agua_e_repeticao(self):
        b = BatalhaNaval(5, (2,), random.Random(0))
        livre = next((l, c) for l in range(5) for c in range(5) if (l, c) not in b.navios[0])
        self.assertEqual(b.atirar(livre), "agua")
        with self.assertRaises(ValueError):
            b.atirar(livre)
        with self.assertRaises(ValueError):
            b.atirar((9, 9))


if __name__ == "__main__":
    unittest.main()
