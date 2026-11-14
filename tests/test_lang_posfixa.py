import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from lang_posfixa import ErroExpressao, avaliar, avaliar_posfixa, infixa_para_posfixa


class TestPosfixa(unittest.TestCase):
    def test_conversao_basica(self):
        self.assertEqual(infixa_para_posfixa("a + b * c"), ["a", "b", "c", "*", "+"])
        self.assertEqual(infixa_para_posfixa("(a + b) * c"), ["a", "b", "+", "c", "*"])
        self.assertEqual(infixa_para_posfixa("a - b - c"), ["a", "b", "-", "c", "-"])

    def test_potencia_associa_a_direita(self):
        self.assertEqual(infixa_para_posfixa("a ^ b ^ c"), ["a", "b", "c", "^", "^"])
        self.assertEqual(avaliar("2 ^ 3 ^ 2"), 512)

    def test_unario(self):
        self.assertEqual(infixa_para_posfixa("-a + b"), ["a", "u-", "b", "+"])
        self.assertEqual(avaliar("-2 ^ 2"), -4)
        self.assertEqual(avaliar("3 * -2"), -6)
        self.assertEqual(avaliar("2 - -3"), 5)

    def test_avaliacao(self):
        self.assertEqual(avaliar("3 + 4 * 2 / ( 1 - 5 ) ^ 2 ^ 3"), 3 + 4 * 2 / (1 - 5) ** 2 ** 3)
        self.assertEqual(avaliar("x * 2 + y", {"x": 3, "y": 1}), 7)
        self.assertEqual(avaliar("10 % 4"), 2)

    def test_posfixa_direta(self):
        self.assertEqual(avaliar_posfixa(["5", "1", "2", "+", "4", "*", "+", "3", "-"]), 14)

    def test_erros_infixa(self):
        for e in ["", "1 +", "(1", "1)", "1 2", "* 2", "()", "1 $ 2", "(1)(2)", "1 + * 2"]:
            with self.assertRaises(ErroExpressao, msg=e):
                infixa_para_posfixa(e)

    def test_erros_avaliacao(self):
        with self.assertRaises(ErroExpressao):
            avaliar("1 / 0")
        with self.assertRaises(ErroExpressao):
            avaliar("a + 1")
        with self.assertRaises(ErroExpressao):
            avaliar_posfixa(["1", "+"])
        with self.assertRaises(ErroExpressao):
            avaliar_posfixa(["1", "2"])


if __name__ == "__main__":
    unittest.main()
