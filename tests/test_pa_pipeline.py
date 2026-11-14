import itertools
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from pa_pipeline import Pipeline


class TestPipeline(unittest.TestCase):
    def test_encadeamento(self):
        r = Pipeline(range(10)).filtrar(lambda x: x % 2).mapear(lambda x: x * x).para_lista()
        self.assertEqual(r, [1, 9, 25, 49, 81])

    def test_preguicoso_com_fonte_infinita(self):
        r = Pipeline(itertools.count()).mapear(lambda x: x + 1).pegar(3).para_lista()
        self.assertEqual(r, [1, 2, 3])

    def test_pegar_zero_nao_consome(self):
        consumidos = []

        def fonte():
            for i in range(5):
                consumidos.append(i)
                yield i

        self.assertEqual(Pipeline(fonte()).pegar(0).para_lista(), [])
        self.assertEqual(consumidos, [])

    def test_pegar_negativo(self):
        with self.assertRaises(ValueError):
            Pipeline([1]).pegar(-1)

    def test_achatar(self):
        self.assertEqual(Pipeline([[1, 2], [], [3]]).achatar().para_lista(), [1, 2, 3])

    def test_vazio_e_iteravel(self):
        self.assertEqual(list(Pipeline([])), [])


if __name__ == "__main__":
    unittest.main()
