import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from txt_silabas import contar_silabas, dividir_silabas


class TestSilabas(unittest.TestCase):
    def test_simples(self):
        self.assertEqual(dividir_silabas("casa"), ["ca", "sa"])
        self.assertEqual(dividir_silabas("palavra"), ["pa", "la", "vra"])

    def test_consoantes_juntas(self):
        self.assertEqual(dividir_silabas("instante"), ["ins", "tan", "te"])
        self.assertEqual(dividir_silabas("carro"), ["car", "ro"])
        self.assertEqual(dividir_silabas("coelho"), ["co", "e", "lho"])

    def test_hiato_e_ditongo(self):
        self.assertEqual(dividir_silabas("saída"), ["sa", "í", "da"])
        self.assertEqual(dividir_silabas("queijo"), ["quei", "jo"])
        self.assertEqual(contar_silabas("mão"), 1)
        self.assertEqual(contar_silabas("pneu"), 1)

    def test_contagem(self):
        self.assertEqual(contar_silabas("computador"), 4)
        self.assertEqual(contar_silabas("a"), 1)

    def test_bordas(self):
        self.assertEqual(dividir_silabas(""), [])
        self.assertEqual(dividir_silabas("123"), [])
        self.assertEqual(dividir_silabas("psc"), ["psc"])
        self.assertEqual("".join(dividir_silabas("Extraordinário")), "extraordinário")


if __name__ == "__main__":
    unittest.main()
