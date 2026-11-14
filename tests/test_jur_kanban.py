import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from jur_kanban import Kanban


class TestKanban(unittest.TestCase):
    def test_fluxo(self):
        k = Kanban()
        k.adicionar("P1")
        self.assertEqual(k.coluna_de("P1"), "triagem")
        self.assertEqual(k.avancar("P1"), "peticionar")
        k.mover("P1", "audiencia")
        self.assertEqual(k.quadro()["audiencia"], ["P1"])
        self.assertEqual(k.contagem()["triagem"], 0)

    def test_duplicado_e_inexistente(self):
        k = Kanban()
        k.adicionar("P1")
        with self.assertRaises(ValueError):
            k.adicionar("P1")
        with self.assertRaises(KeyError):
            k.coluna_de("X")
        with self.assertRaises(KeyError):
            k.adicionar("P2", "nao-existe")

    def test_wip(self):
        k = Kanban(limites={"peticionar": 1})
        k.adicionar("A", "peticionar")
        with self.assertRaises(ValueError):
            k.adicionar("B", "peticionar")
        k.adicionar("B")
        with self.assertRaises(ValueError):
            k.mover("B", "peticionar")
        self.assertEqual(k.coluna_de("B"), "triagem")  # estado preservado após falha

    def test_mover_mesma_coluna_ignora_limite(self):
        k = Kanban(limites={"triagem": 1})
        k.adicionar("A")
        k.mover("A", "triagem")
        self.assertEqual(k.contagem()["triagem"], 1)

    def test_ultima_coluna(self):
        k = Kanban(["a", "b"])
        k.adicionar("P")
        k.avancar("P")
        with self.assertRaises(ValueError):
            k.avancar("P")

    def test_remover(self):
        k = Kanban()
        k.adicionar("P")
        k.remover("P")
        with self.assertRaises(KeyError):
            k.remover("P")

    def test_config_invalida(self):
        with self.assertRaises(ValueError):
            Kanban(["a", "a"])
        with self.assertRaises(ValueError):
            Kanban(["a"], {"z": 1})

    def test_quadro_e_copia(self):
        k = Kanban()
        k.adicionar("P")
        k.quadro()["triagem"].clear()
        self.assertEqual(k.contagem()["triagem"], 1)


if __name__ == "__main__":
    unittest.main()
