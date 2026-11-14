import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fp_resultado import Err, Ok, particionar, recuperar, sequence, tentar, traverse, unit


def dividir(x):
    return Err("div0") if x == 0 else Ok(100 / x)


def positivo(x):
    return Ok(x) if x > 0 else Err("negativo")


class TestResultado(unittest.TestCase):
    def test_leis_monad(self):
        self.assertEqual(unit(4).bind(dividir), dividir(4))
        for r in (Ok(5), Err("e"), Ok(0)):
            self.assertEqual(r.bind(unit), r)
            self.assertEqual(
                r.bind(dividir).bind(positivo),
                r.bind(lambda x: dividir(x).bind(positivo)),
            )

    def test_functor(self):
        for r in (Ok(2), Err("x")):
            self.assertEqual(r.map(lambda x: x), r)
        f, g = (lambda x: x + 1), (lambda x: x * 2)
        self.assertEqual(Ok(3).map(lambda x: g(f(x))), Ok(3).map(f).map(g))

    def test_err_curto_circuita(self):
        chamadas = []
        r = Err("falha").bind(lambda x: chamadas.append(x) or Ok(x))
        self.assertEqual(r, Err("falha"))
        self.assertEqual(chamadas, [])

    def test_map_err_e_get_or(self):
        self.assertEqual(Err("a").map_err(str.upper), Err("A"))
        self.assertEqual(Ok(1).map_err(str.upper), Ok(1))
        self.assertEqual(Err("a").get_or(7), 7)
        self.assertEqual(Ok(1).get_or(7), 1)

    def test_tentar(self):
        self.assertEqual(tentar(int, "12"), Ok(12))
        r = tentar(int, "x")
        self.assertIsInstance(r, Err)
        self.assertIsInstance(r.erro, ValueError)
        with self.assertRaises(ZeroDivisionError):
            tentar(lambda: 1 / 0, excecoes=(ValueError,))

    def test_sequence_traverse(self):
        self.assertEqual(sequence([Ok(1), Ok(2)]), Ok([1, 2]))
        self.assertEqual(sequence([Ok(1), Err("a"), Err("b")]), Err("a"))
        self.assertEqual(traverse(positivo, [1, -1, 2]), Err("negativo"))
        self.assertEqual(traverse(positivo, []), Ok([]))

    def test_particionar_recuperar_dobrar(self):
        self.assertEqual(particionar([Ok(1), Err("a"), Ok(2)]), ([1, 2], ["a"]))
        self.assertEqual(recuperar(Err("a"), lambda e: Ok(e * 2)), Ok("aa"))
        self.assertEqual(recuperar(Ok(1), lambda e: Ok(0)), Ok(1))
        self.assertEqual(Ok(1).dobrar(str, lambda v: v + 1), 2)
        self.assertEqual(Err(1).dobrar(lambda e: "E", str), "E")
        self.assertEqual(Ok(lambda x: x + 1).ap(Ok(1)), Ok(2))


if __name__ == "__main__":
    unittest.main()
