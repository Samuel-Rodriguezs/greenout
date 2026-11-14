import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ml_filtro_colaborativo import (FiltroColaborativo, similaridade_cosseno,
                                    similaridade_pearson)

NOTAS = {
    "ana": {"matrix": 5, "alien": 4, "titanic": 1},
    "bia": {"matrix": 5, "alien": 5, "blade": 4},
    "caio": {"matrix": 1, "titanic": 5, "up": 5},
    "dani": {"titanic": 5, "up": 4, "matrix": 2},
    "edu": {"cafe": 3},
}


class TestFiltro(unittest.TestCase):
    def test_cosseno(self):
        self.assertAlmostEqual(similaridade_cosseno({"a": 1, "b": 1}, {"a": 2, "b": 2}), 1.0)
        self.assertEqual(similaridade_cosseno({"a": 1}, {"b": 1}), 0.0)

    def test_pearson(self):
        a = {"x": 1, "y": 2, "z": 3}
        self.assertAlmostEqual(similaridade_pearson(a, {"x": 2, "y": 4, "z": 6}), 1.0)
        self.assertAlmostEqual(similaridade_pearson(a, {"x": 3, "y": 2, "z": 1}), -1.0)
        self.assertEqual(similaridade_pearson({"x": 1}, {"x": 1}), 0.0)
        self.assertEqual(similaridade_pearson({"x": 1, "y": 1}, {"x": 1, "y": 2}), 0.0)

    def test_vizinho_mais_proximo(self):
        f = FiltroColaborativo(NOTAS)
        viz = f.vizinhos("ana", k=2)
        self.assertEqual(viz[0][0], "bia")
        self.assertNotIn("edu", [u for u, _ in f.vizinhos("ana", k=10)])

    def test_prever_item_do_vizinho(self):
        f = FiltroColaborativo(NOTAS)
        self.assertAlmostEqual(f.prever("ana", "blade", k=1), 4.0)

    def test_prever_sem_informacao(self):
        self.assertIsNone(FiltroColaborativo(NOTAS).prever("ana", "cafe"))

    def test_recomendar_exclui_vistos_e_ordena(self):
        rec = FiltroColaborativo(NOTAS).recomendar("ana", n=5, k=3)
        itens = [i for i, _ in rec]
        self.assertNotIn("matrix", itens)
        self.assertIn("blade", itens)
        self.assertEqual([n for _, n in rec], sorted((n for _, n in rec), reverse=True))

    def test_usuario_desconhecido(self):
        with self.assertRaises(KeyError):
            FiltroColaborativo(NOTAS).vizinhos("zed")


if __name__ == "__main__":
    unittest.main()
