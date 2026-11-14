import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_gilded_rose import BACKSTAGE, BRIE, SULFURAS, Item, atualizar_qualidade


def um_dia(nome: str, prazo: int, qualidade: int) -> Item:
    item = Item(nome, prazo, qualidade)
    atualizar_qualidade([item])
    return item


class TestCaracterizacao(unittest.TestCase):
    """Testes de caracterização do comportamento do código legado."""

    def test_item_comum(self):
        i = um_dia("Elixir", 5, 10)
        self.assertEqual((i.prazo, i.qualidade), (4, 9))

    def test_item_comum_vencido_degrada_dobrado(self):
        i = um_dia("Elixir", 0, 10)
        self.assertEqual((i.prazo, i.qualidade), (-1, 8))

    def test_qualidade_nunca_negativa(self):
        self.assertEqual(um_dia("Elixir", 3, 0).qualidade, 0)
        self.assertEqual(um_dia("Elixir", 0, 1).qualidade, 0)

    def test_brie_aumenta(self):
        self.assertEqual(um_dia(BRIE, 5, 10).qualidade, 11)

    def test_brie_vencido_aumenta_dobrado(self):
        self.assertEqual(um_dia(BRIE, 0, 10).qualidade, 12)

    def test_brie_limite_50(self):
        self.assertEqual(um_dia(BRIE, 5, 50).qualidade, 50)
        self.assertEqual(um_dia(BRIE, 0, 49).qualidade, 50)

    def test_sulfuras_imutavel(self):
        i = um_dia(SULFURAS, 0, 80)
        self.assertEqual((i.prazo, i.qualidade), (0, 80))
        i = um_dia(SULFURAS, -1, 80)
        self.assertEqual((i.prazo, i.qualidade), (-1, 80))

    def test_backstage_longe(self):
        self.assertEqual(um_dia(BACKSTAGE, 11, 20).qualidade, 21)

    def test_backstage_10_dias(self):
        self.assertEqual(um_dia(BACKSTAGE, 10, 20).qualidade, 22)
        self.assertEqual(um_dia(BACKSTAGE, 6, 20).qualidade, 22)

    def test_backstage_5_dias(self):
        self.assertEqual(um_dia(BACKSTAGE, 5, 20).qualidade, 23)
        self.assertEqual(um_dia(BACKSTAGE, 1, 20).qualidade, 23)

    def test_backstage_apos_show(self):
        self.assertEqual(um_dia(BACKSTAGE, 0, 30).qualidade, 0)

    def test_backstage_limite_50(self):
        self.assertEqual(um_dia(BACKSTAGE, 5, 49).qualidade, 50)
        self.assertEqual(um_dia(BACKSTAGE, 10, 49).qualidade, 50)


class TestConjured(unittest.TestCase):
    def test_degrada_dobrado(self):
        self.assertEqual(um_dia("Conjured Mana Cake", 3, 6).qualidade, 4)

    def test_vencido_degrada_quadruplo(self):
        self.assertEqual(um_dia("Conjured Mana Cake", 0, 6).qualidade, 2)

    def test_nao_fica_negativo(self):
        self.assertEqual(um_dia("Conjured Mana Cake", 0, 3).qualidade, 0)


class TestVariosDias(unittest.TestCase):
    def test_simulacao_30_dias(self):
        itens = [Item("Elixir", 10, 20), Item(BRIE, 2, 0), Item(SULFURAS, 0, 80),
                 Item(BACKSTAGE, 15, 20), Item("Conjured Mana Cake", 3, 6)]
        for _ in range(30):
            atualizar_qualidade(itens)
        elixir, brie, sulf, back, conj = itens
        self.assertEqual((elixir.prazo, elixir.qualidade), (-20, 0))
        self.assertEqual((brie.prazo, brie.qualidade), (-28, 50))
        self.assertEqual((sulf.prazo, sulf.qualidade), (0, 80))
        self.assertEqual((back.prazo, back.qualidade), (-15, 0))
        self.assertEqual((conj.prazo, conj.qualidade), (-27, 0))

    def test_backstage_ate_o_show(self):
        item = Item(BACKSTAGE, 15, 20)
        for _ in range(15):
            atualizar_qualidade([item])
        self.assertEqual(item.qualidade, 50)
        atualizar_qualidade([item])
        self.assertEqual(item.qualidade, 0)


if __name__ == "__main__":
    unittest.main()
