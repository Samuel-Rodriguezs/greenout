import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from pa_bits import (bit_menos_significativo, contar_bits, eh_potencia_de_dois,
                     inverter_bits, subconjuntos, trocar_sem_temporaria, unico_elemento)


class TestBits(unittest.TestCase):
    def test_potencia_de_dois(self):
        self.assertTrue(all(eh_potencia_de_dois(1 << i) for i in range(20)))
        self.assertFalse(any(eh_potencia_de_dois(n) for n in (0, -4, 3, 6, 12)))

    def test_contar_bits(self):
        self.assertEqual(contar_bits(0), 0)
        self.assertEqual(contar_bits(255), 8)
        self.assertEqual(contar_bits(0b101010), 3)
        for n in range(200):
            self.assertEqual(contar_bits(n), bin(n).count("1"))
        with self.assertRaises(ValueError):
            contar_bits(-1)

    def test_bit_menos_significativo(self):
        self.assertEqual(bit_menos_significativo(12), 4)
        self.assertEqual(bit_menos_significativo(0), 0)

    def test_trocar(self):
        self.assertEqual(trocar_sem_temporaria(3, 9), (9, 3))
        self.assertEqual(trocar_sem_temporaria(5, 5), (5, 5))

    def test_inverter_bits(self):
        self.assertEqual(inverter_bits(0b00000001), 0b10000000)
        self.assertEqual(inverter_bits(0b110, 3), 0b011)
        with self.assertRaises(ValueError):
            inverter_bits(256)
        with self.assertRaises(ValueError):
            inverter_bits(1, 0)

    def test_unico(self):
        self.assertEqual(unico_elemento([4, 1, 2, 1, 2]), 4)
        self.assertEqual(unico_elemento([7]), 7)

    def test_subconjuntos(self):
        s = subconjuntos([1, 2, 3])
        self.assertEqual(len(s), 8)
        self.assertEqual(s[0], [])
        self.assertIn([1, 3], s)
        self.assertEqual(subconjuntos([]), [[]])


if __name__ == "__main__":
    unittest.main()
