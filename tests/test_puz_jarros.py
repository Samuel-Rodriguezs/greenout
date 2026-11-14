import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from puz_jarros import possivel_dois_jarros, resolver, sucessores


def executar(caps, ops):
    estado = (0,) * len(caps)
    for op in ops:
        estado = dict(sucessores(estado, caps))[op]
    return estado


class TestJarros(unittest.TestCase):
    def test_classico_3_5_4(self):
        sol = resolver((3, 5), 4)
        self.assertEqual(len(sol), 6)
        self.assertIn(4, executar((3, 5), sol))

    def test_die_hard_5_3_4_ordem_invertida(self):
        sol = resolver((5, 3), 4)
        self.assertEqual(len(sol), 6)

    def test_alvo_ja_igual_capacidade(self):
        self.assertEqual(resolver((3, 5), 5), ["encher 1"])

    def test_alvo_zero(self):
        self.assertEqual(resolver((3, 5), 0), [])

    def test_impossivel(self):
        self.assertIsNone(resolver((4, 6), 5))   # mdc 2
        self.assertIsNone(resolver((3, 5), 6))   # maior que tudo

    def test_tres_jarros(self):
        sol = resolver((8, 5, 3), 4)
        self.assertIn(4, executar((8, 5, 3), sol))

    def test_criterio_bezout_coerente_com_bfs(self):
        for a, b in [(3, 5), (4, 6), (2, 7), (6, 9)]:
            for alvo in range(1, max(a, b) + 1):
                self.assertEqual(resolver((a, b), alvo) is not None, possivel_dois_jarros(a, b, alvo))

    def test_invalido(self):
        with self.assertRaises(ValueError):
            resolver((0, 3), 1)


if __name__ == "__main__":
    unittest.main()
