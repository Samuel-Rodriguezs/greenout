import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from crip_elgamal import cifrar, decifrar, gerar_chaves, gerar_primo_seguro
from crip_rsa import eh_primo


class TestElGamal(unittest.TestCase):
    def test_primo_seguro(self):
        p = gerar_primo_seguro(24, random.Random(3))
        self.assertTrue(eh_primo(p))
        self.assertTrue(eh_primo((p - 1) // 2))

    def test_ida_e_volta(self):
        rng = random.Random(11)
        pub, priv = gerar_chaves(32, rng)
        for m in (1, 2, 4242, pub.p - 1):
            self.assertEqual(decifrar(cifrar(m, pub, rng), priv), m)

    def test_probabilistico(self):
        rng = random.Random(5)
        pub, _ = gerar_chaves(32, rng)
        self.assertNotEqual(cifrar(777, pub, rng), cifrar(777, pub, rng))

    def test_homomorfismo_multiplicativo(self):
        rng = random.Random(9)
        pub, priv = gerar_chaves(32, rng)
        a, b = cifrar(12, pub, rng), cifrar(7, pub, rng)
        prod = (a[0] * b[0] % pub.p, a[1] * b[1] % pub.p)
        self.assertEqual(decifrar(prod, priv), 84)

    def test_mensagem_invalida(self):
        pub, _ = gerar_chaves(24, random.Random(1))
        for m in (0, pub.p):
            with self.assertRaises(ValueError):
                cifrar(m, pub)


if __name__ == "__main__":
    unittest.main()
