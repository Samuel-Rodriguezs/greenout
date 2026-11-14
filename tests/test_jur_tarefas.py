import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from jur_tarefas import FilaTarefas, Prioridade


class TestTarefas(unittest.TestCase):
    def test_ordem(self):
        f = FilaTarefas()
        f.adicionar("baixa", Prioridade.BAIXA)
        f.adicionar("normal sem prazo")
        f.adicionar("normal com prazo", prazo=date(2024, 6, 1))
        f.adicionar("urgente", Prioridade.URGENTE)
        f.adicionar("normal sem prazo 2")
        self.assertEqual([t.titulo for t in f.pendentes()],
                         ["urgente", "normal com prazo", "normal sem prazo", "normal sem prazo 2", "baixa"])
        self.assertEqual(f.proxima().titulo, "urgente")
        self.assertEqual(len(f), 4)

    def test_fifo_na_igualdade(self):
        f = FilaTarefas()
        for n in "abc":
            f.adicionar(n)
        self.assertEqual([f.proxima().titulo for _ in range(3)], ["a", "b", "c"])
        self.assertIsNone(f.proxima())

    def test_cancelar(self):
        f = FilaTarefas()
        a = f.adicionar("a", Prioridade.URGENTE)
        f.adicionar("b")
        f.cancelar(a.id)
        self.assertEqual(f.espiar().titulo, "b")
        self.assertEqual(len(f), 1)
        with self.assertRaises(KeyError):
            f.cancelar(a.id)
        with self.assertRaises(KeyError):
            f.cancelar(99)

    def test_por_responsavel(self):
        f = FilaTarefas()
        f.adicionar("x", Prioridade.URGENTE, "Ana")
        f.adicionar("y", Prioridade.BAIXA, "Bia")
        f.adicionar("z", Prioridade.NORMAL, "Bia")
        self.assertEqual(f.proxima("Bia").titulo, "z")
        self.assertIsNone(f.proxima("Carlos"))
        self.assertEqual([t.titulo for t in f.pendentes()], ["x", "y"])

    def test_atrasadas(self):
        f = FilaTarefas()
        f.adicionar("velha", prazo=date(2024, 1, 1))
        f.adicionar("futura", prazo=date(2024, 12, 1))
        f.adicionar("sem prazo")
        self.assertEqual([t.titulo for t in f.atrasadas(date(2024, 6, 1))], ["velha"])

    def test_titulo_vazio(self):
        with self.assertRaises(ValueError):
            FilaTarefas().adicionar("  ")


if __name__ == "__main__":
    unittest.main()
