import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fp_trie_persistente import MapaPersistente


class ChaveColidente:
    """Todas as instâncias têm o mesmo hash; igualdade por id lógico."""

    def __init__(self, n):
        self.n = n

    def __hash__(self):
        return 42

    def __eq__(self, o):
        return isinstance(o, ChaveColidente) and o.n == self.n


class ChaveProxima:
    """Hashes que coincidem nos 10 bits baixos, forçando nós profundos."""

    def __init__(self, n):
        self.n = n

    def __hash__(self):
        return (self.n << 10) | 0b1111111111

    def __eq__(self, o):
        return isinstance(o, ChaveProxima) and o.n == self.n


class TestMapaPersistente(unittest.TestCase):
    def test_basico(self):
        m = MapaPersistente().com("a", 1).com("b", 2)
        self.assertEqual(m["a"], 1)
        self.assertEqual(m.get("b"), 2)
        self.assertEqual(m.get("z", 0), 0)
        self.assertIn("a", m)
        self.assertNotIn("z", m)
        self.assertEqual(len(m), 2)
        with self.assertRaises(KeyError):
            m["z"]

    def test_persistencia(self):
        v0 = MapaPersistente()
        v1 = v0.com("x", 1)
        v2 = v1.com("x", 2).com("y", 3)
        v3 = v2.sem("x")
        self.assertEqual(len(v0), 0)
        self.assertEqual(v1.para_dict(), {"x": 1})
        self.assertEqual(v2.para_dict(), {"x": 2, "y": 3})
        self.assertEqual(v3.para_dict(), {"y": 3})
        self.assertEqual(len(v1.com("x", 9)), 1)  # sobrescrever não cresce

    def test_compartilhamento_estrutural(self):
        m = MapaPersistente.de_dict({i: i for i in range(200)})
        n = m.com(1000, 1)
        iguais = sum(1 for a, b in zip(m._raiz.filhos, n._raiz.filhos) if a is b)
        self.assertGreater(iguais, 20)  # quase todos os subnós reaproveitados

    def test_remocao(self):
        m = MapaPersistente.de_dict({"a": 1, "b": 2})
        self.assertIs(m.sem("zzz"), m)
        self.assertEqual(len(m.sem("a")), 1)
        self.assertEqual(len(m.sem("a").sem("b")), 0)
        self.assertEqual(MapaPersistente().sem("a"), MapaPersistente())
        self.assertEqual(m.sem("a").sem("b"), MapaPersistente())

    def test_colisao_total_de_hash(self):
        m = MapaPersistente()
        for i in range(5):
            m = m.com(ChaveColidente(i), i * 10)
        self.assertEqual(len(m), 5)
        self.assertEqual(m[ChaveColidente(3)], 30)
        m = m.com(ChaveColidente(3), -1)
        self.assertEqual(len(m), 5)
        self.assertEqual(m[ChaveColidente(3)], -1)
        m = m.sem(ChaveColidente(0)).sem(ChaveColidente(1)).sem(ChaveColidente(2)).sem(ChaveColidente(3))
        self.assertEqual(len(m), 1)
        self.assertEqual(m[ChaveColidente(4)], 40)
        self.assertNotIn(ChaveColidente(0), m)
        self.assertEqual(len(m.sem(ChaveColidente(4))), 0)

    def test_hashes_proximos_geram_nos_profundos(self):
        m = MapaPersistente()
        for i in range(50):
            m = m.com(ChaveProxima(i), i)
        for i in range(50):
            self.assertEqual(m[ChaveProxima(i)], i)
        for i in range(0, 50, 2):
            m = m.sem(ChaveProxima(i))
        self.assertEqual(len(m), 25)
        self.assertNotIn(ChaveProxima(2), m)
        self.assertIn(ChaveProxima(3), m)

    def test_aleatorio_contra_dict(self):
        rng = random.Random(7)
        ref, m = {}, MapaPersistente()
        historico = []
        for _ in range(3000):
            k = rng.randint(0, 400)
            if rng.random() < 0.65:
                v = rng.random()
                ref[k] = v
                m = m.com(k, v)
            else:
                ref.pop(k, None)
                m = m.sem(k)
            historico.append((dict(ref), m))
        self.assertEqual(m.para_dict(), ref)
        self.assertEqual(len(m), len(ref))
        for d, mapa in historico[::300]:  # versões antigas continuam intactas
            self.assertEqual(mapa.para_dict(), d)

    def test_iteracao_igualdade_imutavel(self):
        m = MapaPersistente.de_dict({1: "a", 2: "b"})
        self.assertEqual(sorted(m), [1, 2])
        self.assertEqual(sorted(m.items()), [(1, "a"), (2, "b")])
        self.assertEqual(m, MapaPersistente().com(2, "b").com(1, "a"))
        self.assertNotEqual(m, MapaPersistente())
        self.assertNotEqual(m, {1: "a", 2: "b"})
        with self.assertRaises(AttributeError):
            m.x = 1
        with self.assertRaises(TypeError):
            hash(m)
        self.assertEqual(MapaPersistente().com(None, 0)[None], 0)


if __name__ == "__main__":
    unittest.main()
