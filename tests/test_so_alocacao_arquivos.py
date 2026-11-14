import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from so_alocacao_arquivos import FAT, FIM, Contigua, Encadeada, SemEspaco


def cenario(cls):
    d = cls(10)
    d.criar("A", 3)  # 0-2
    d.criar("B", 2)  # 3-4
    d.criar("C", 3)  # 5-7
    d.remover("B")
    return d


class TestAlocacaoArquivos(unittest.TestCase):
    def test_contigua_fragmentacao_externa(self):
        d = cenario(Contigua)
        self.assertEqual(d.livres(), [3, 4, 8, 9])  # 4 livres, mas em dois buracos
        with self.assertRaises(SemEspaco):
            d.criar("D", 3)
        self.assertEqual(d.criar("E", 2), [3, 4])

    def test_encadeada_usa_buracos(self):
        d = cenario(Encadeada)
        self.assertEqual(d.criar("D", 3), [3, 4, 8])
        self.assertEqual(d.blocos("D"), [3, 4, 8])
        self.assertEqual(d.proximo[3], 4)
        self.assertEqual(d.proximo[4], 8)
        self.assertEqual(d.proximo[8], FIM)

    def test_fat_tabela(self):
        d = cenario(FAT)
        d.criar("D", 3)
        self.assertEqual(d.tabela[3:5] + [d.tabela[8]], [4, 8, FIM])
        self.assertEqual(d.livres(), [9])

    def test_leituras_para_alcancar_bloco(self):
        for cls, esperado in ((Contigua, 1), (Encadeada, 3), (FAT, 1)):
            with self.subTest(cls=cls.__name__):
                d = cls(10)
                d.criar("f", 4)
                self.assertEqual(d.leituras_ate("f", 2), esperado)
        d = Encadeada(10)
        d.criar("f", 4)
        self.assertEqual([d.leituras_ate("f", i) for i in range(4)], [1, 2, 3, 4])

    def test_estender_contigua_bloqueada(self):
        d = Contigua(10)
        d.criar("A", 3)
        d.criar("B", 3)
        with self.assertRaises(SemEspaco):
            d.estender("A", 1)  # bloco 3 pertence a B
        self.assertEqual(d.estender("B", 2), [6, 7])
        with self.assertRaises(SemEspaco):
            d.estender("B", 3)  # passaria do fim do disco

    def test_estender_encadeada_cresce_em_qualquer_lugar(self):
        d = Encadeada(8)
        d.criar("A", 2)  # 0,1
        d.criar("B", 2)  # 2,3
        d.estender("A", 2)  # 4,5
        self.assertEqual(d.blocos("A"), [0, 1, 4, 5])
        self.assertEqual(d.blocos("B"), [2, 3])

    def test_remover_libera_tudo(self):
        for cls in (Contigua, Encadeada, FAT):
            d = cls(6)
            d.criar("x", 6)
            d.remover("x")
            self.assertEqual(d.livres(), list(range(6)))

    def test_erros(self):
        d = Encadeada(4)
        d.criar("a", 3)
        with self.assertRaises(SemEspaco):
            d.criar("b", 2)
        with self.assertRaises(ValueError):
            d.criar("a", 1)
        with self.assertRaises(ValueError):
            d.criar("c", 0)
        with self.assertRaises(KeyError):
            d.blocos("nada")
        with self.assertRaises(IndexError):
            d.leituras_ate("a", 3)


if __name__ == "__main__":
    unittest.main()
