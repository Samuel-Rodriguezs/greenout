import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from jur_duplicidade import Registro, duplicados_por_numero, similaridade, suspeitos

A = Registro("a", "0001234-56.2024.8.26.0100", ("João", "Banco X"), "indenização por dano moral cobrança indevida")
B = Registro("b", "00012345620248260100", ("joão", "banco x"), "outro")
C = Registro("c", "0009999-11.2024.8.26.0100", ("João ", "Banco X"), "indenização por dano moral cobrança indevida")
D = Registro("d", "0005555-22.2024.8.26.0100", ("Maria", "Loja Y"), "despejo por falta de pagamento")


class TestDuplicidade(unittest.TestCase):
    def test_mesmo_numero_mascaras_diferentes(self):
        self.assertEqual(duplicados_por_numero([A, B, C, D]), [["a", "b"]])

    def test_sem_duplicados(self):
        self.assertEqual(duplicados_por_numero([A, C, D]), [])
        self.assertEqual(duplicados_por_numero([]), [])

    def test_similaridade(self):
        self.assertEqual(similaridade(A, C), 1.0)
        self.assertLess(similaridade(A, D), 0.1)  # só compartilham a palavra "por"
        self.assertEqual(similaridade(Registro("x", "1"), Registro("y", "2")), 0.0)

    def test_suspeitos(self):
        self.assertEqual(suspeitos([A, B, C, D]), [("a", "c", 1.0)])

    def test_limite_menor_pega_parcial(self):
        s = suspeitos([A, B, C, D], limite=0.5)
        self.assertIn(("b", "c"), [(x, y) for x, y, _ in s])
        self.assertNotIn(("a", "b"), [(x, y) for x, y, _ in s])  # mesmo número: não é suspeito, é duplicado

    def test_limite_invalido(self):
        with self.assertRaises(ValueError):
            suspeitos([A], limite=0)


if __name__ == "__main__":
    unittest.main()
