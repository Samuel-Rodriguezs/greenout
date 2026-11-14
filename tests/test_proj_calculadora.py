import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from proj_calculadora import avaliar, tokenizar, ErroCalculo


class TestCalculadora(unittest.TestCase):
    def test_precedencia(self):
        self.assertEqual(avaliar("2 + 3 * 4"), 14)
        self.assertEqual(avaliar("(2 + 3) * 4"), 20)

    def test_potencia_associa_direita(self):
        self.assertEqual(avaliar("2 ^ 3 ^ 2"), 512)

    def test_unario(self):
        self.assertEqual(avaliar("-3 + 5"), 2)
        self.assertEqual(avaliar("--4"), 4)
        self.assertEqual(avaliar("2 * -3"), -6)

    def test_decimais(self):
        self.assertAlmostEqual(avaliar("1.5 * 2 + .5"), 3.5)

    def test_tokenizar(self):
        self.assertEqual(tokenizar("12+(3*4)"), ["12", "+", "(", "3", "*", "4", ")"])

    def test_erros(self):
        for expr in ("1 / 0", "2 +", "(1 + 2", "1 2", "3 $ 4", ""):
            with self.subTest(expr=expr):
                with self.assertRaises(ErroCalculo):
                    avaliar(expr)


if __name__ == "__main__":
    unittest.main()
