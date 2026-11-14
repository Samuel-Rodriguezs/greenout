import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from proj_agenda import Agenda


class TestAgenda(unittest.TestCase):
    def setUp(self):
        self.a = Agenda()
        self.a.adicionar("Maria Silva", "(11) 98888-7777", "maria@x.com")
        self.a.adicionar("Mario Souza", "11 97777-6666")

    def test_obter_normaliza_telefone(self):
        c = self.a.obter("maria silva")
        self.assertEqual(c.telefone, "11988887777")

    def test_buscar_ordenado(self):
        self.assertEqual([c.nome for c in self.a.buscar("mar")], ["Maria Silva", "Mario Souza"])
        self.assertEqual(self.a.buscar("zzz"), [])

    def test_remover(self):
        self.a.remover("Mario Souza")
        self.assertEqual(len(self.a), 1)
        with self.assertRaises(KeyError):
            self.a.obter("Mario Souza")

    def test_duplicado(self):
        with self.assertRaises(ValueError):
            self.a.adicionar("MARIA SILVA", "11999999999")

    def test_validacoes(self):
        with self.assertRaises(ValueError):
            self.a.adicionar("", "11999999999")
        with self.assertRaises(ValueError):
            self.a.adicionar("Ana", "123")
        with self.assertRaises(ValueError):
            self.a.adicionar("Ana", "11999999999", "invalido")

    def test_remover_inexistente(self):
        with self.assertRaises(KeyError):
            self.a.remover("Ninguem")


if __name__ == "__main__":
    unittest.main()
