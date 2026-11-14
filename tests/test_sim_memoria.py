import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sim_memoria import JogoMemoria


class TestMemoria(unittest.TestCase):
    def test_embaralhamento_deterministico(self):
        a = JogoMemoria(list("ABCD"), random.Random(1)).cartas
        b = JogoMemoria(list("ABCD"), random.Random(1)).cartas
        self.assertEqual(a, b)
        self.assertEqual(sorted(a), sorted(list("ABCD") * 2))

    def test_par_e_erro(self):
        j = JogoMemoria(list("ABC"), random.Random(2))
        i = 0
        k = next(x for x in range(1, 6) if j.cartas[x] == j.cartas[0])
        outro = next(x for x in range(1, 6) if j.cartas[x] != j.cartas[0])
        self.assertEqual(j.virar(i), "primeira")
        self.assertEqual(j.virar(outro), "erro")
        self.assertEqual(j.virar(i), "primeira")
        self.assertEqual(j.virar(k), "par")
        self.assertEqual(j.encontradas, {i, k})
        self.assertEqual(j.tentativas, 2)

    def test_jogo_completo(self):
        j = JogoMemoria(list("ABCD"), random.Random(5))
        pos: dict[str, list[int]] = {}
        for idx, c in enumerate(j.cartas):
            pos.setdefault(c, []).append(idx)
        for a, b in pos.values():
            j.virar(a)
            j.virar(b)
        self.assertTrue(j.terminou)
        self.assertEqual(j.tentativas, 4)

    def test_erros(self):
        j = JogoMemoria(["A"], random.Random(1))
        with self.assertRaises(IndexError):
            j.virar(9)
        j.virar(0)
        with self.assertRaises(ValueError):
            j.virar(0)
        with self.assertRaises(ValueError):
            JogoMemoria(["A", "A"])


if __name__ == "__main__":
    unittest.main()
