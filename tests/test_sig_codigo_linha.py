import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import sig_codigo_linha as c

BITS = [1, 0, 1, 1, 0, 0, 1]


class TestCodigoLinha(unittest.TestCase):
    def test_nrz(self):
        self.assertEqual(c.nrz_codificar([1, 0, 1]), [1, -1, 1])
        self.assertEqual(c.nrz_decodificar(c.nrz_codificar(BITS)), BITS)

    def test_manchester(self):
        self.assertEqual(c.manchester_codificar([1, 0]), [-1, 1, 1, -1])
        self.assertEqual(c.manchester_decodificar(c.manchester_codificar(BITS)), BITS)

    def test_manchester_violacao(self):
        with self.assertRaises(ValueError):
            c.manchester_decodificar([1, 1])
        with self.assertRaises(ValueError):
            c.manchester_decodificar([1, -1, 1])

    def test_manchester_sempre_tem_transicao_por_bit(self):
        n = c.manchester_codificar([0, 0, 0, 0])
        self.assertGreaterEqual(c.transicoes(n), 4)
        self.assertEqual(c.transicoes(c.nrz_codificar([0, 0, 0, 0])), 0)

    def test_ami(self):
        self.assertEqual(c.ami_codificar([1, 0, 1, 1, 0, 1]), [1, 0, -1, 1, 0, -1])
        self.assertEqual(c.ami_decodificar(c.ami_codificar(BITS)), BITS)

    def test_ami_violacao(self):
        with self.assertRaises(ValueError):
            c.ami_decodificar([1, 0, 1])
        with self.assertRaises(ValueError):
            c.ami_decodificar([2])

    def test_ami_dc_nulo(self):
        self.assertEqual(sum(c.ami_codificar([1] * 10)), 0)

    def test_bits_invalidos(self):
        for f in (c.nrz_codificar, c.manchester_codificar, c.ami_codificar):
            with self.assertRaises(ValueError):
                f([0, 2])

    def test_forma_de_onda(self):
        self.assertEqual(c.para_forma_de_onda([1, -1], 3), [1, 1, 1, -1, -1, -1])
        with self.assertRaises(ValueError):
            c.para_forma_de_onda([1], 0)

    def test_vazios(self):
        self.assertEqual(c.manchester_codificar([]), [])
        self.assertEqual(c.ami_decodificar([]), [])
        self.assertEqual(c.transicoes([1]), 0)


if __name__ == "__main__":
    unittest.main()
