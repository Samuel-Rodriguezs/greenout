import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import gen_ids_sortaveis as g


class Relogio:
    def __init__(self, t: int) -> None:
        self.t = t

    def __call__(self) -> int:
        return self.t


class TestGenIdsSortaveis(unittest.TestCase):
    def test_codificar_decodificar(self):
        for v in (0, 1, 31, 32, 1 << 47, g.MAX_TEMPO):
            self.assertEqual(g.decodificar(g.codificar(v, 10)), v)
        self.assertEqual(g.codificar(0, 3), "000")
        self.assertEqual(g.codificar(31, 1), "Z")
        with self.assertRaises(ValueError):
            g.codificar(32, 1)
        with self.assertRaises(ValueError):
            g.decodificar("U")

    def test_formato_e_tempo(self):
        r = Relogio(1_700_000_000_000)
        u = g.GeradorUlid(random.Random(1), r).proximo()
        self.assertEqual(len(u), 26)
        self.assertTrue(set(u) <= set(g.ALFABETO))
        self.assertEqual(g.tempo_do_ulid(u), 1_700_000_000_000)

    def test_ordem_lexicografica_acompanha_o_tempo(self):
        r = Relogio(1000)
        ger = g.GeradorUlid(random.Random(2), r)
        ids = []
        for _ in range(200):
            r.t += random.Random(r.t).randint(0, 3)  # avança 0..3 ms (inclui mesmo ms)
            ids.append(ger.proximo())
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(len(set(ids)), 200)

    def test_mesmo_milissegundo_incrementa(self):
        r = Relogio(5000)
        ger = g.GeradorUlid(random.Random(3), r)
        a, b, c = ger.proximo(), ger.proximo(), ger.proximo()
        self.assertEqual(a[:10], b[:10])
        self.assertEqual(g.decodificar(b[10:]), g.decodificar(a[10:]) + 1)
        self.assertEqual(g.decodificar(c[10:]), g.decodificar(a[10:]) + 2)

    def test_relogio_recua_continua_monotonico(self):
        r = Relogio(9000)
        ger = g.GeradorUlid(random.Random(4), r)
        a = ger.proximo()
        r.t = 8000
        b = ger.proximo()
        self.assertGreater(b, a)
        self.assertEqual(g.tempo_do_ulid(b), 9000)

    def test_determinismo(self):
        def serie(seed):
            r = Relogio(123)
            ger = g.GeradorUlid(random.Random(seed), r)
            out = []
            for i in range(20):
                r.t += i % 3
                out.append(ger.proximo())
            return out

        self.assertEqual(serie(7), serie(7))
        self.assertNotEqual(serie(7), serie(8))

    def test_overflow_e_tempo_invalido(self):
        class RngMax(random.Random):
            def getrandbits(self, k):
                return (1 << k) - 1

        ger = g.GeradorUlid(RngMax(), Relogio(1))
        ger.proximo()
        with self.assertRaises(OverflowError):
            ger.proximo()
        with self.assertRaises(ValueError):
            g.GeradorUlid(random.Random(0), Relogio(-5)).proximo()
        with self.assertRaises(ValueError):
            g.tempo_do_ulid("curto")


if __name__ == "__main__":
    unittest.main()
