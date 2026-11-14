import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from pa_rpn import ErroRPN, avaliar_rpn


class TestRPN(unittest.TestCase):
    def test_basico(self):
        self.assertEqual(avaliar_rpn("3 4 +"), 7)
        self.assertEqual(avaliar_rpn("5 1 2 + 4 * + 3 -"), 14)

    def test_ordem_dos_operandos(self):
        self.assertEqual(avaliar_rpn("10 4 -"), 6)
        self.assertEqual(avaliar_rpn("2 3 ^"), 8)
        self.assertEqual(avaliar_rpn("9 2 /"), 4.5)

    def test_comandos_de_pilha(self):
        self.assertEqual(avaliar_rpn("3 dup *"), 9)
        self.assertEqual(avaliar_rpn("1 2 swap -"), 1)
        self.assertEqual(avaliar_rpn("1 2 drop"), 1)

    def test_erros(self):
        for expr in ["", "1 2", "+", "1 +", "1 0 /", "1 x +", "drop"]:
            with self.subTest(expr=expr):
                with self.assertRaises(ErroRPN):
                    avaliar_rpn(expr)

    def test_decimais_e_negativos(self):
        self.assertEqual(avaliar_rpn("-1.5 2 *"), -3)


if __name__ == "__main__":
    unittest.main()
