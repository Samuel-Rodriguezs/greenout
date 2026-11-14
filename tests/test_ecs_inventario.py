import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_inventario import Inventario, Item, transferir

POCAO = Item("pocao", "Poção", peso=0.5, max_pilha=5)
ESPADA = Item("espada", "Espada", peso=4.0)


class TestInventario(unittest.TestCase):
    def test_empilha_e_abre_novas_pilhas(self):
        inv = Inventario(3)
        self.assertEqual(inv.adicionar(POCAO, 7), 0)
        self.assertEqual(inv.slot(0), (POCAO, 5))
        self.assertEqual(inv.slot(1), (POCAO, 2))
        inv.adicionar(POCAO, 2)
        self.assertEqual(inv.slot(1), (POCAO, 4))
        self.assertEqual(inv.contar("pocao"), 9)

    def test_sem_espaco_devolve_sobra(self):
        inv = Inventario(2)
        self.assertEqual(inv.adicionar(POCAO, 12), 2)
        self.assertEqual(inv.contar("pocao"), 10)
        self.assertEqual(inv.adicionar(ESPADA), 1)

    def test_limite_de_peso(self):
        inv = Inventario(10, peso_max=10)
        self.assertEqual(inv.adicionar(ESPADA, 3), 1)
        self.assertEqual(inv.peso, 8)
        self.assertEqual(inv.adicionar(POCAO, 10), 6)  # só cabem 4 (2.0 kg)
        self.assertEqual(inv.peso, 10)

    def test_remover_tudo_ou_nada(self):
        inv = Inventario(3)
        inv.adicionar(POCAO, 7)
        inv.remover("pocao", 3)
        self.assertEqual(inv.contar("pocao"), 4)
        with self.assertRaises(ValueError):
            inv.remover("pocao", 5)
        self.assertEqual(inv.contar("pocao"), 4)
        inv.remover("pocao", 4)
        self.assertEqual(inv.livres(), 3)

    def test_mover_trocar_e_unir(self):
        inv = Inventario(3)
        inv.adicionar(ESPADA)
        inv.adicionar(POCAO, 3)
        inv.mover(0, 1)
        self.assertEqual(inv.slot(0), (POCAO, 3))
        self.assertEqual(inv.slot(1), (ESPADA, 1))
        inv.adicionar(POCAO, 3)  # completa 0 -> 5 e cria pilha de 1 no slot 2
        inv.mover(2, 0)
        self.assertEqual(inv.slot(0), (POCAO, 5))
        self.assertEqual(inv.slot(2), (POCAO, 1))
        inv.mover(1, 1)

    def test_dividir(self):
        inv = Inventario(3)
        inv.adicionar(POCAO, 5)
        j = inv.dividir(0, 2)
        self.assertEqual((inv.slot(0), inv.slot(j)), ((POCAO, 3), (POCAO, 2)))
        with self.assertRaises(ValueError):
            inv.dividir(0, 3)

    def test_organizar(self):
        inv = Inventario(5)
        inv.adicionar(POCAO, 3)
        inv.adicionar(ESPADA)
        inv.adicionar(POCAO, 4)
        inv.remover("espada")
        inv.mover(0, 3)
        inv.organizar()
        self.assertEqual([inv.slot(i) for i in range(3)], [(POCAO, 5), (POCAO, 2), None])
        self.assertEqual(inv.contar("pocao"), 7)

    def test_transferir(self):
        a, b = Inventario(5), Inventario(1, peso_max=None)
        a.adicionar(POCAO, 8)
        self.assertEqual(transferir(a, b, "pocao", 8), 5)
        self.assertEqual((a.contar("pocao"), b.contar("pocao")), (3, 5))
        self.assertEqual(transferir(a, b, "espada", 1), 0)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            Inventario(0)
        with self.assertRaises(ValueError):
            Inventario(1).adicionar(POCAO, -1)


if __name__ == "__main__":
    unittest.main()
