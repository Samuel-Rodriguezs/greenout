import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from pa_cache_ttl import cache_ttl


class TestCacheTtl(unittest.TestCase):
    def setUp(self):
        self.t = [0.0]
        self.chamadas = 0

        @cache_ttl(10, relogio=lambda: self.t[0])
        def f(x, y=1):
            self.chamadas += 1
            return x * y

        self.f = f

    def test_usa_cache_dentro_do_ttl(self):
        self.assertEqual(self.f(2), 2)
        self.t[0] = 9.9
        self.assertEqual(self.f(2), 2)
        self.assertEqual(self.chamadas, 1)

    def test_expira(self):
        self.f(2)
        self.t[0] = 10
        self.f(2)
        self.assertEqual(self.chamadas, 2)

    def test_chaves_distintas_e_kwargs(self):
        self.f(2)
        self.f(2, y=3)
        self.f(3)
        self.assertEqual(self.chamadas, 3)

    def test_limpar(self):
        self.f(1)
        self.f.limpar()
        self.f(1)
        self.assertEqual(self.chamadas, 2)

    def test_ttl_invalido(self):
        with self.assertRaises(ValueError):
            cache_ttl(0)

    def test_preserva_nome(self):
        self.assertEqual(self.f.__name__, "f")


if __name__ == "__main__":
    unittest.main()
