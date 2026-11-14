import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from pa_funcional import aplicar_parcial, caminhos_grade, compor, produto


class TestFuncional(unittest.TestCase):
    def test_compor_ordem(self):
        f = compor(lambda x: x + 1, lambda x: x * 2)
        self.assertEqual(f(5), 11)

    def test_compor_vazio_e_unico(self):
        self.assertEqual(compor()(7), 7)
        self.assertEqual(compor(str)(7), "7")

    def test_compor_primeira_funcao_multiplos_args(self):
        self.assertEqual(compor(str, lambda a, b: a + b)(1, 2), "3")

    def test_parcial(self):
        dobro = aplicar_parcial(pow, 2)
        self.assertEqual(dobro(10), 1024)
        self.assertEqual(aplicar_parcial(int, base=2)("101"), 5)

    def test_produto(self):
        self.assertEqual(produto([2, 3, 4]), 24)
        self.assertEqual(produto([]), 1)

    def test_caminhos_grade(self):
        self.assertEqual(caminhos_grade(3, 3), 6)
        self.assertEqual(caminhos_grade(1, 9), 1)
        self.assertEqual(caminhos_grade(18, 18), 2333606220)

    def test_caminhos_grade_invalido(self):
        with self.assertRaises(ValueError):
            caminhos_grade(0, 3)

    def test_cache_ativo(self):
        caminhos_grade.cache_clear()
        caminhos_grade(10, 10)
        self.assertGreater(caminhos_grade.cache_info().hits, 0)


if __name__ == "__main__":
    unittest.main()
