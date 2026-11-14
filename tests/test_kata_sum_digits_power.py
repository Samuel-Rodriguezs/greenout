import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_sum_digits_power import eh_potencia_digitos, primeiros, soma_potencias


class TestKataSumDigitsPower(unittest.TestCase):
    def test_soma_potencias(self):
        self.assertEqual(soma_potencias(89), 8 + 81)
        self.assertEqual(soma_potencias(695), 6 + 81 + 125)
        self.assertEqual(soma_potencias(5), 5)
        self.assertEqual(soma_potencias(0), 0)

    def test_soma_potencias_com_inicio(self):
        self.assertEqual(soma_potencias(46288, 3), 4 ** 3 + 6 ** 4 + 2 ** 5 + 8 ** 6 + 8 ** 7)

    def test_multiplos(self):
        self.assertEqual(eh_potencia_digitos(89), 1)
        self.assertEqual(eh_potencia_digitos(92), -1)
        self.assertEqual(eh_potencia_digitos(695, 2), 2)
        self.assertEqual(eh_potencia_digitos(46288, 3), 51)
        self.assertEqual(eh_potencia_digitos(46288), -1)

    def test_digitos_unicos(self):
        for d in range(1, 10):
            self.assertEqual(eh_potencia_digitos(d), 1)

    def test_primeiros(self):
        self.assertEqual(primeiros(0), [])
        self.assertEqual(primeiros(3), [89, 135, 175])
        self.assertEqual(primeiros(6), [89, 135, 175, 518, 598, 1306])

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            soma_potencias(-1)
        with self.assertRaises(ValueError):
            eh_potencia_digitos(0)
        with self.assertRaises(ValueError):
            primeiros(-1)


if __name__ == "__main__":
    unittest.main()
