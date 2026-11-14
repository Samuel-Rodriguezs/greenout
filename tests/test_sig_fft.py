import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import sig_fft as f


def proximos(a, b, tol=1e-9):
    return len(a) == len(b) and all(abs(x - y) < tol for x, y in zip(a, b))


class TestFFT(unittest.TestCase):
    def test_impulso(self):
        self.assertTrue(proximos(f.fft([1, 0, 0, 0]), [1, 1, 1, 1]))

    def test_constante(self):
        self.assertTrue(proximos(f.fft([1, 1, 1, 1]), [4, 0, 0, 0]))

    def test_exemplo_conhecido(self):
        self.assertTrue(proximos(f.fft([1, 2, 3, 4]), [10, -2 + 2j, -2, -2 - 2j]))

    def test_fft_igual_dft(self):
        x = [math.sin(i) + 0.3 * i for i in range(16)]
        self.assertTrue(proximos(f.fft(x), f.dft(x), 1e-8))

    def test_inversas(self):
        x = [complex(i, -i / 2) for i in range(8)]
        self.assertTrue(proximos(f.ifft(f.fft(x)), x))
        self.assertTrue(proximos(f.idft(f.dft(x)), x))

    def test_parseval(self):
        x = [math.cos(0.7 * i) for i in range(32)]
        X = f.fft(x)
        self.assertAlmostEqual(sum(v * v for v in x), sum(abs(v) ** 2 for v in X) / 32)

    def test_tamanho_invalido(self):
        with self.assertRaises(ValueError):
            f.fft([1, 2, 3])

    def test_zero_pad(self):
        self.assertEqual(len(f.fft_zero_pad([1, 2, 3])), 4)
        self.assertEqual(f.proxima_potencia_de_dois(5), 8)
        self.assertTrue(f.potencia_de_dois(1))
        self.assertFalse(f.potencia_de_dois(0))

    def test_tamanho_um(self):
        self.assertTrue(proximos(f.fft([5]), [5]))


if __name__ == "__main__":
    unittest.main()
