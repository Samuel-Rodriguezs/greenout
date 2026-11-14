import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_fizzbuzz_whiz import REGRAS_WHIZ, Regra, converter, gerar


class TestKataFizzBuzzWhiz(unittest.TestCase):
    def test_classico(self):
        self.assertEqual(list(gerar(1, 15)), [
            "1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz",
            "11", "Fizz", "13", "14", "FizzBuzz",
        ])

    def test_whiz(self):
        self.assertEqual(converter(7, REGRAS_WHIZ), "Whiz")
        self.assertEqual(converter(21, REGRAS_WHIZ), "FizzWhiz")
        self.assertEqual(converter(35, REGRAS_WHIZ), "BuzzWhiz")
        self.assertEqual(converter(105, REGRAS_WHIZ), "FizzBuzzWhiz")
        self.assertEqual(converter(11, REGRAS_WHIZ), "11")

    def test_regras_customizadas(self):
        regras = (Regra("Foo", divisor=2), Regra("Bar", divisor=4))
        self.assertEqual(converter(2, regras), "Foo")
        self.assertEqual(converter(8, regras), "FooBar")
        self.assertEqual(converter(3, regras), "3")

    def test_ordem_das_regras_define_ordem_da_palavra(self):
        regras = (Regra("Buzz", divisor=5), Regra("Fizz", divisor=3))
        self.assertEqual(converter(15, regras), "BuzzFizz")

    def test_digito_sem_prioridade_concatena(self):
        regras = (Regra("Fizz", divisor=3), Regra("Fizz", digito=3))
        self.assertEqual(converter(13, regras), "Fizz")
        self.assertEqual(converter(33, regras), "FizzFizz")

    def test_digito_com_prioridade(self):
        regras = (Regra("Fizz", divisor=3), Regra("Buzz", divisor=5), Regra("Fizz", digito=3))
        self.assertEqual(converter(13, regras, prioridade_digito=True), "Fizz")
        self.assertEqual(converter(35, regras, prioridade_digito=True), "Fizz")
        self.assertEqual(converter(10, regras, prioridade_digito=True), "Buzz")

    def test_digito_zero(self):
        self.assertEqual(converter(10, (Regra("Zero", digito=0),)), "Zero")

    def test_negativo(self):
        self.assertEqual(converter(-3), "Fizz")
        self.assertEqual(converter(-13, (Regra("T", digito=3),)), "T")

    def test_sem_regras(self):
        self.assertEqual(converter(3, ()), "3")

    def test_regras_invalidas(self):
        with self.assertRaises(ValueError):
            Regra("X")
        with self.assertRaises(ValueError):
            Regra("X", divisor=2, digito=3)
        with self.assertRaises(ValueError):
            Regra("X", divisor=0)
        with self.assertRaises(ValueError):
            Regra("X", digito=10)
        with self.assertRaises(ValueError):
            Regra("", divisor=2)


if __name__ == "__main__":
    unittest.main()
