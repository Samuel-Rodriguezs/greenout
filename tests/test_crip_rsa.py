import random
import sys
import unittest
from math import gcd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from crip_rsa import (
    assinar, cifrar, decifrar, eh_primo, euclides_estendido, gerar_chaves, gerar_primo, inverso_modular, verificar,
)


class TestRsa(unittest.TestCase):
    def test_euclides(self):
        g, x, y = euclides_estendido(240, 46)
        self.assertEqual(g, 2)
        self.assertEqual(240 * x + 46 * y, 2)

    def test_inverso(self):
        self.assertEqual(inverso_modular(3, 11), 4)
        with self.assertRaises(ValueError):
            inverso_modular(6, 9)

    def test_miller_rabin(self):
        primos = [p for p in range(2, 2000) if all(p % d for d in range(2, int(p**0.5) + 1))]
        self.assertEqual([n for n in range(2000) if eh_primo(n)], primos)
        self.assertTrue(eh_primo(2**61 - 1))
        self.assertFalse(eh_primo(561))  # Carmichael
        self.assertFalse(eh_primo(3215031751))  # pseudoprimo forte em várias bases

    def test_gerar_primo(self):
        p = gerar_primo(20, random.Random(1))
        self.assertTrue(eh_primo(p))
        self.assertEqual(p.bit_length(), 20)

    def test_ida_e_volta(self):
        rng = random.Random(42)
        n, e, d = gerar_chaves(24, rng)
        for m in (0, 1, 2, 12345, n - 1):
            self.assertEqual(decifrar(cifrar(m, n, e), n, d), m)
        with self.assertRaises(ValueError):
            cifrar(n, n, e)

    def test_exemplo_classico(self):
        # p=61, q=53 -> n=3233, e=17, d=2753
        self.assertEqual(cifrar(65, 3233, 17), 2790)
        self.assertEqual(decifrar(2790, 3233, 2753), 65)
        self.assertEqual(gcd(17, 60 * 52), 1)

    def test_assinatura(self):
        n, e, d = gerar_chaves(24, random.Random(7))
        s = assinar(999, n, d)
        self.assertTrue(verificar(999, s, n, e))
        self.assertFalse(verificar(1000, s, n, e))


if __name__ == "__main__":
    unittest.main()
