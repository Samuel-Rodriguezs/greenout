import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_video_store import Aluguel, Categoria, Cliente, Filme

REGULAR = Filme("Casablanca", Categoria.REGULAR)
NOVO = Filme("Duna 2", Categoria.LANCAMENTO)
INFANTIL = Filme("Moana", Categoria.INFANTIL)


class TestKataVideoStore(unittest.TestCase):
    def test_regular(self):
        self.assertEqual(Aluguel(REGULAR, 1).valor(), 2.0)
        self.assertEqual(Aluguel(REGULAR, 2).valor(), 2.0)
        self.assertEqual(Aluguel(REGULAR, 3).valor(), 3.5)
        self.assertEqual(Aluguel(REGULAR, 6).valor(), 8.0)

    def test_lancamento(self):
        self.assertEqual(Aluguel(NOVO, 1).valor(), 3.0)
        self.assertEqual(Aluguel(NOVO, 4).valor(), 12.0)

    def test_infantil(self):
        self.assertEqual(Aluguel(INFANTIL, 1).valor(), 1.5)
        self.assertEqual(Aluguel(INFANTIL, 3).valor(), 1.5)
        self.assertEqual(Aluguel(INFANTIL, 4).valor(), 3.0)
        self.assertEqual(Aluguel(INFANTIL, 5).valor(), 4.5)

    def test_pontos(self):
        self.assertEqual(Aluguel(REGULAR, 5).pontos(), 1)
        self.assertEqual(Aluguel(NOVO, 1).pontos(), 1)
        self.assertEqual(Aluguel(NOVO, 2).pontos(), 2)
        self.assertEqual(Aluguel(INFANTIL, 9).pontos(), 1)

    def test_cliente_sem_alugueis(self):
        c = Cliente("Ana")
        self.assertEqual(c.total(), 0)
        self.assertEqual(c.pontos(), 0)
        self.assertEqual(c.extrato(),
                         "Extrato de aluguel para Ana\nValor devido: 0.0\n"
                         "Você ganhou 0 pontos de fidelidade")

    def test_extrato_completo(self):
        c = Cliente("Bruno")
        c.alugar(REGULAR, 3)
        c.alugar(NOVO, 2)
        c.alugar(INFANTIL, 4)
        esperado = (
            "Extrato de aluguel para Bruno\n"
            "\tCasablanca\t3.5\n"
            "\tDuna 2\t6.0\n"
            "\tMoana\t3.0\n"
            "Valor devido: 12.5\n"
            "Você ganhou 4 pontos de fidelidade"
        )
        self.assertEqual(c.extrato(), esperado)

    def test_dias_invalidos(self):
        with self.assertRaises(ValueError):
            Aluguel(REGULAR, 0)


if __name__ == "__main__":
    unittest.main()
