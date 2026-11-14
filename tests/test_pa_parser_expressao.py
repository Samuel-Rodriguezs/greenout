import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from pa_parser_expressao import ErroSintaxe, calcular


class TestParser(unittest.TestCase):
    def test_precedencia(self):
        self.assertEqual(calcular("2 + 3 * 4"), 14)
        self.assertEqual(calcular("(2 + 3) * 4"), 20)

    def test_associatividade(self):
        self.assertEqual(calcular("10 - 4 - 3"), 3)
        self.assertEqual(calcular("2 ** 3 ** 2"), 512)
        self.assertEqual(calcular("100 / 10 / 5"), 2)

    def test_unario(self):
        self.assertEqual(calcular("-3 + 5"), 2)
        self.assertEqual(calcular("--3"), 3)
        self.assertEqual(calcular("2 * -3"), -6)

    def test_decimais(self):
        self.assertAlmostEqual(calcular("1.5 * 2"), 3.0)

    def test_erros_de_sintaxe(self):
        for expr in ["", "2 +", "(1 + 2", "1 + 2)", "2 $ 3", "* 3", "1 2"]:
            with self.subTest(expr=expr):
                with self.assertRaises(ErroSintaxe):
                    calcular(expr)

    def test_divisao_por_zero(self):
        with self.assertRaises(ZeroDivisionError):
            calcular("1 / (2 - 2)")


if __name__ == "__main__":
    unittest.main()
