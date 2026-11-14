import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from crip_dh import P_MODP14, derivar_chave, gerar_privada, publica, segredo_compartilhado


class TestDh(unittest.TestCase):
    def test_primo_correto(self):
        self.assertEqual(P_MODP14.bit_length(), 2048)
        self.assertEqual(pow(2, P_MODP14 - 1, P_MODP14), 1)  # Fermat

    def test_acordo(self):
        a, b = gerar_privada(), gerar_privada()
        A, B = publica(a), publica(b)
        s1, s2 = segredo_compartilhado(a, B), segredo_compartilhado(b, A)
        self.assertEqual(s1, s2)
        self.assertEqual(derivar_chave(s1), derivar_chave(s2))
        self.assertEqual(len(derivar_chave(s1)), 32)

    def test_grupo_pequeno_classico(self):
        p, g = 23, 5
        A, B = publica(6, p, g), publica(15, p, g)
        self.assertEqual((A, B), (8, 19))
        self.assertEqual(segredo_compartilhado(6, B, p), 2)
        self.assertEqual(segredo_compartilhado(15, A, p), 2)

    def test_publica_invalida(self):
        for ruim in (0, 1, P_MODP14 - 1, P_MODP14):
            with self.assertRaises(ValueError):
                segredo_compartilhado(5, ruim)


if __name__ == "__main__":
    unittest.main()
