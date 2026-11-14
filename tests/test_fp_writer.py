import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fp_writer import Writer, censurar, collatz, fatorial, mapear_m, ouvir, tell, unit


def dobra(x):
    return Writer(x * 2, (f"dobra {x}",))


def mais1(x):
    return Writer(x + 1, (f"mais1 {x}",))


class TestWriter(unittest.TestCase):
    def test_leis_monad(self):
        self.assertEqual(unit(3).bind(dobra), dobra(3))
        w = Writer(3, ("ini",))
        self.assertEqual(w.bind(unit), w)
        self.assertEqual(
            w.bind(dobra).bind(mais1), w.bind(lambda x: dobra(x).bind(mais1))
        )

    def test_functor_e_ap(self):
        w = Writer(2, ("a",))
        self.assertEqual(w.map(lambda x: x), w)
        r = Writer(lambda x: x + 1, ("f",)).ap(Writer(1, ("x",)))
        self.assertEqual(r, Writer(2, ("f", "x")))

    def test_ordem_do_log(self):
        w = unit(1).bind(dobra).bind(mais1)
        self.assertEqual(w.executar(), (3, ("dobra 1", "mais1 2")))

    def test_tell_censurar_ouvir(self):
        self.assertEqual(tell("a", "b").log, ("a", "b"))
        self.assertEqual(censurar(tell("a", "b"), lambda l: l[:1]).log, ("a",))
        self.assertEqual(ouvir(tell("x")).valor, (None, ("x",)))

    def test_fatorial(self):
        valor, log = fatorial(4).executar()
        self.assertEqual(valor, 24)
        self.assertEqual(len(log), 5)
        self.assertEqual(log[0], "fatorial(0) = 1")
        self.assertEqual(fatorial(0).valor, 1)
        with self.assertRaises(ValueError):
            fatorial(-1)

    def test_collatz_e_mapear_m(self):
        valor, log = collatz(6).executar()
        self.assertEqual(log, (6, 3, 10, 5, 16, 8, 4, 2, 1))
        self.assertEqual(valor, 8)
        self.assertEqual(collatz(1).executar(), (0, (1,)))
        w = mapear_m(dobra, [1, 2, 3])
        self.assertEqual(w.valor, [2, 4, 6])
        self.assertEqual(len(w.log), 3)
        self.assertEqual(mapear_m(dobra, []), Writer([], ()))


if __name__ == "__main__":
    unittest.main()
