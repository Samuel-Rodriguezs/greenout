import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from puz_mastermind import avaliar, pior_caso, resolver, todos_codigos


class TestMastermind(unittest.TestCase):
    def test_avaliar(self):
        self.assertEqual(avaliar((1, 2, 3, 4), (1, 2, 3, 4)), (4, 0))
        self.assertEqual(avaliar((1, 2, 3, 4), (4, 3, 2, 1)), (0, 4))
        self.assertEqual(avaliar((1, 1, 2, 2), (1, 2, 1, 3)), (1, 2))
        self.assertEqual(avaliar((0, 0, 0, 0), (1, 1, 1, 1)), (0, 0))

    def test_avaliar_repeticoes(self):
        # só uma cor 1 no segredo: o segundo 1 do palpite não conta como branco
        self.assertEqual(avaliar((1, 0, 0, 0), (1, 1, 2, 2)), (1, 0))
        self.assertEqual(avaliar((1, 0, 0, 0), (2, 1, 1, 2)), (0, 1))

    def test_tamanhos_diferentes(self):
        with self.assertRaises(ValueError):
            avaliar((1, 2), (1, 2, 3))

    def test_resolve_todos_3_cores_3_posicoes(self):
        for s in todos_codigos(3, 3):
            hist = resolver(s, 3, 3)
            self.assertEqual(hist[-1], s)
            self.assertEqual(len(set(hist)), len(hist))

    def test_penultimo_palpite_consistente(self):
        segredo = (2, 0, 3, 1)
        hist = resolver(segredo, 4, 4)
        self.assertEqual(hist[-1], segredo)
        # o palpite final precisa ser consistente com todas as respostas anteriores
        for anterior in hist[:-1]:
            self.assertEqual(avaliar(hist[-1], anterior), avaliar(segredo, anterior))

    def test_pior_caso_pequeno(self):
        self.assertLessEqual(pior_caso(4, 3), 5)

    def test_classico_6_cores_resolve_em_poucos_palpites(self):
        for segredo in [(0, 0, 0, 0), (5, 4, 3, 2), (1, 3, 3, 5)]:
            self.assertLessEqual(len(resolver(segredo)), 6)

    def test_segredo_invalido(self):
        with self.assertRaises(ValueError):
            resolver((0, 9, 0, 0), 6, 4)


if __name__ == "__main__":
    unittest.main()
