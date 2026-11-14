import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from rede_balde import LeakyBucket, TokenBucket


class Relogio:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


class TestRedeBalde(unittest.TestCase):
    def test_token_rajada_e_esgotamento(self):
        r = Relogio()
        b = TokenBucket(taxa=2, capacidade=5, relogio=r)
        self.assertEqual([b.consumir() for _ in range(6)], [True] * 5 + [False])

    def test_token_reabastece(self):
        r = Relogio()
        b = TokenBucket(2, 5, r)
        b.consumir(5)
        r.t = 1.0
        self.assertEqual(b.tokens, 2.0)
        self.assertTrue(b.consumir(2))
        self.assertFalse(b.consumir())

    def test_token_nao_excede_capacidade(self):
        r = Relogio()
        b = TokenBucket(10, 3, r)
        r.t = 100
        self.assertEqual(b.tokens, 3.0)

    def test_token_pedido_grande(self):
        b = TokenBucket(1, 4)
        self.assertFalse(b.consumir(5))
        self.assertEqual(b.tokens, 4.0)  # nada consumido
        with self.assertRaises(ValueError):
            b.espera(5)

    def test_token_espera(self):
        r = Relogio()
        b = TokenBucket(4, 8, r)
        b.consumir(8)
        self.assertEqual(b.espera(2), 0.5)
        r.t = 0.5
        self.assertEqual(b.espera(2), 0.0)

    def test_leaky_enche_e_descarta(self):
        r = Relogio()
        b = LeakyBucket(taxa=1, capacidade=3, relogio=r)
        self.assertEqual([b.adicionar() for _ in range(4)], [True, True, True, False])

    def test_leaky_escoa(self):
        r = Relogio()
        b = LeakyBucket(2, 4, r)
        b.adicionar(4)
        r.t = 1.5
        self.assertEqual(b.nivel, 1.0)
        self.assertTrue(b.adicionar(3))
        r.t = 100
        self.assertEqual(b.nivel, 0.0)

    def test_leaky_atraso(self):
        r = Relogio()
        b = LeakyBucket(4, 10, r)
        b.adicionar(8)
        self.assertEqual(b.atraso(), 2.0)

    def test_leaky_suaviza_rajada_token_nao(self):
        r = Relogio()
        tb, lb = TokenBucket(1, 5, r), LeakyBucket(1, 5, r)
        self.assertEqual(sum(tb.consumir() for _ in range(5)), 5)  # rajada passa inteira
        self.assertEqual(lb.nivel, 0.0)
        for _ in range(5):
            lb.adicionar()
        self.assertEqual(lb.atraso(), 5.0)  # mas sai a taxa constante

    def test_invalidos(self):
        for cls in (TokenBucket, LeakyBucket):
            with self.assertRaises(ValueError):
                cls(0, 1)
            with self.assertRaises(ValueError):
                cls(1, -1)


if __name__ == "__main__":
    unittest.main()
