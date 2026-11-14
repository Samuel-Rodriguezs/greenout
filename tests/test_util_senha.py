import string
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from util_senha import SIMBOLOS, gerar_senha


class TestSenha(unittest.TestCase):
    def test_tamanho(self):
        for n in (4, 8, 16, 100):
            self.assertEqual(len(gerar_senha(n)), n)

    def test_todas_as_classes(self):
        for _ in range(200):
            s = gerar_senha(4)
            self.assertTrue(any(c in string.ascii_lowercase for c in s))
            self.assertTrue(any(c in string.ascii_uppercase for c in s))
            self.assertTrue(any(c in string.digits for c in s))
            self.assertTrue(any(c in SIMBOLOS for c in s))

    def test_sem_simbolos(self):
        for _ in range(100):
            s = gerar_senha(3, simbolos=False)
            self.assertTrue(s.isalnum())

    def test_tamanho_invalido(self):
        with self.assertRaises(ValueError):
            gerar_senha(3)
        with self.assertRaises(ValueError):
            gerar_senha(2, simbolos=False)
        with self.assertRaises(ValueError):
            gerar_senha(2000)

    def test_senhas_diferentes(self):
        self.assertEqual(len({gerar_senha(20) for _ in range(50)}), 50)


if __name__ == "__main__":
    unittest.main()
