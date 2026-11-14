import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_decorator import Cafe, Caramelo, Chantilly, Leite


class TestDecorator(unittest.TestCase):
    def test_simples(self):
        c = Cafe()
        self.assertEqual((c.descricao(), c.preco()), ("cafe", Decimal("5.00")))

    def test_empilhado(self):
        b = Chantilly(Leite(Cafe()))
        self.assertEqual(b.descricao(), "cafe + leite + chantilly")
        self.assertEqual(b.preco(), Decimal("8.75"))

    def test_repetido(self):
        b = Caramelo(Caramelo(Cafe()))
        self.assertEqual(b.preco(), Decimal("7.00"))
        self.assertEqual(b.descricao(), "cafe + caramelo + caramelo")


if __name__ == "__main__":
    unittest.main()
