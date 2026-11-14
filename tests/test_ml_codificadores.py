import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ml_codificadores import LabelEncoder, OneHotEncoder

CORES = ["verde", "azul", "verde", "vermelho", "azul"]


class TestCodificadores(unittest.TestCase):
    def test_label(self):
        le = LabelEncoder()
        self.assertEqual(le.ajustar_transformar(CORES), [1, 0, 1, 2, 0])
        self.assertEqual(le.classes, ["azul", "verde", "vermelho"])
        self.assertEqual(le.inverter([2, 0]), ["vermelho", "azul"])

    def test_label_desconhecido(self):
        le = LabelEncoder().ajustar(CORES)
        with self.assertRaises(ValueError):
            le.transformar(["roxo"])
        with self.assertRaises(ValueError):
            le.inverter([5])

    def test_label_inteiros(self):
        self.assertEqual(LabelEncoder().ajustar_transformar([10, 2, 10]), [1, 0, 1])

    def test_onehot(self):
        oh = OneHotEncoder().ajustar(CORES)
        m = oh.transformar(["azul", "vermelho"])
        self.assertEqual(m, [[1, 0, 0], [0, 0, 1]])
        self.assertEqual(oh.categorias, ["azul", "verde", "vermelho"])

    def test_onehot_roundtrip(self):
        oh = OneHotEncoder()
        self.assertEqual(oh.inverter(oh.ajustar_transformar(CORES)), CORES)

    def test_onehot_desconhecido(self):
        oh = OneHotEncoder().ajustar(CORES)
        with self.assertRaises(ValueError):
            oh.transformar(["roxo"])
        self.assertEqual(OneHotEncoder(True).ajustar(CORES).transformar(["roxo"]), [[0, 0, 0]])

    def test_inverter_invalido(self):
        oh = OneHotEncoder().ajustar(CORES)
        with self.assertRaises(ValueError):
            oh.inverter([[1, 1, 0]])

    def test_vazio(self):
        self.assertEqual(OneHotEncoder().ajustar_transformar([]), [])


if __name__ == "__main__":
    unittest.main()
