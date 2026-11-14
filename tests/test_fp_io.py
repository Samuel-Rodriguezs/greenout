import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fp_io import IO, Console, escrever, ler_linha, programa_eco, repetir, sequence, unit


class TestIO(unittest.TestCase):
    def test_nada_executa_antes_de_executar(self):
        c = Console()
        prog = escrever(c, "a").depois(escrever(c, "b"))
        self.assertEqual(c.saidas, [])
        prog.executar()
        self.assertEqual(c.saidas, ["a", "b"])
        prog.executar()  # reexecutável
        self.assertEqual(c.saidas, ["a", "b", "a", "b"])

    def test_leis_monad(self):
        f = lambda x: unit(x + 1)
        g = lambda x: unit(x * 2)
        self.assertEqual(unit(3).bind(f).executar(), f(3).executar())
        m = unit(5)
        self.assertEqual(m.bind(unit).executar(), m.executar())
        self.assertEqual(
            m.bind(f).bind(g).executar(), m.bind(lambda x: f(x).bind(g)).executar()
        )

    def test_leis_com_efeitos_mesma_ordem(self):
        def traco(c, nome):
            return lambda x: IO(lambda: (c.saidas.append(nome), x + 1)[1])
        c1, c2 = Console(), Console()
        m1 = unit(0).bind(traco(c1, "f")).bind(traco(c1, "g"))
        m2 = unit(0).bind(lambda x: traco(c2, "f")(x).bind(traco(c2, "g")))
        self.assertEqual(m1.executar(), m2.executar())
        self.assertEqual(c1.saidas, c2.saidas)

    def test_functor_e_ap(self):
        self.assertEqual(unit(2).map(lambda x: x * 3).executar(), 6)
        self.assertEqual(unit(lambda x: x + 1).ap(unit(1)).executar(), 2)

    def test_eco(self):
        c = Console(entradas=["Ana"])
        programa_eco(c).executar()
        self.assertEqual(c.saidas, ["Olá, Ana!"])

    def test_eof(self):
        with self.assertRaises(EOFError):
            ler_linha(Console()).executar()

    def test_sequence_repetir(self):
        c = Console(entradas=["1", "2", "3"])
        self.assertEqual(repetir(3, ler_linha(c)).executar(), ["1", "2", "3"])
        c2 = Console(entradas=["x", "y"])
        self.assertEqual(sequence([ler_linha(c2), ler_linha(c2)]).executar(), ["x", "y"])
        self.assertEqual(sequence([]).executar(), [])
        self.assertEqual(repetir(0, unit(1)).executar(), [])


if __name__ == "__main__":
    unittest.main()
