import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from web_sessoes import ArmazemSessoes


class Relogio:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


class TestWebSessoes(unittest.TestCase):
    def setUp(self):
        self.rel = Relogio()
        ids = iter(f"id{i}" for i in range(100))
        self.a = ArmazemSessoes(ttl=10, relogio=self.rel, gerar_id=lambda: next(ids))

    def test_criar_e_obter(self):
        s = self.a.criar({"u": 1})
        self.assertEqual(self.a.obter(s.id).dados, {"u": 1})
        self.assertIsNone(self.a.obter("nada"))
        self.assertIsNone(self.a.obter(None))

    def test_expira(self):
        s = self.a.criar()
        self.rel.t = 10
        self.assertIsNone(self.a.obter(s.id))
        self.assertEqual(len(self.a), 0)

    def test_deslizante_renova(self):
        s = self.a.criar()
        self.rel.t = 6
        self.assertIsNotNone(self.a.obter(s.id))
        self.rel.t = 12
        self.assertIsNotNone(self.a.obter(s.id))

    def test_duracao_maxima(self):
        a = ArmazemSessoes(ttl=10, relogio=self.rel, duracao_maxima=15)
        s = a.criar()
        self.rel.t = 8
        self.assertIsNotNone(a.obter(s.id))
        self.rel.t = 16
        self.assertIsNone(a.obter(s.id))

    def test_nao_deslizante(self):
        a = ArmazemSessoes(ttl=10, relogio=self.rel, deslizante=False)
        s = a.criar()
        self.rel.t = 6
        a.obter(s.id)
        self.rel.t = 11
        self.assertIsNone(a.obter(s.id))

    def test_destruir_e_regenerar(self):
        s = self.a.criar({"x": 1})
        nova = self.a.regenerar(s.id)
        self.assertNotEqual(nova.id, s.id)
        self.assertEqual(nova.dados, {"x": 1})
        self.assertIsNone(self.a.obter(s.id))
        self.assertTrue(self.a.destruir(nova.id))
        self.assertFalse(self.a.destruir(nova.id))
        self.assertIsNone(self.a.regenerar("zzz"))

    def test_limpar(self):
        self.a.criar()
        self.rel.t = 5
        self.a.criar()
        self.rel.t = 11
        self.assertEqual(self.a.limpar_expiradas(), 1)
        self.assertEqual(len(self.a), 1)

    def test_ttl_invalido(self):
        with self.assertRaises(ValueError):
            ArmazemSessoes(ttl=0)

    def test_id_padrao_unico(self):
        a = ArmazemSessoes()
        self.assertNotEqual(a.criar().id, a.criar().id)


if __name__ == "__main__":
    unittest.main()
