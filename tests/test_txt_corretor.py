import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from txt_corretor import Corretor


class TestCorretor(unittest.TestCase):
    def setUp(self):
        self.c = Corretor()

    def test_palavra_correta_inalterada(self):
        self.assertEqual(self.c.corrigir("casa"), "casa")

    def test_edicao_simples(self):
        self.assertEqual(self.c.corrigir("casaa"), "casa")
        self.assertEqual(self.c.corrigir("tempp"), "tempo")
        self.assertEqual(self.c.corrigir("obrigdo"), "obrigado")
        self.assertEqual(self.c.corrigir("tambem"), "também")

    def test_troca_de_letras(self):
        self.assertEqual(self.c.corrigir("jnaela"), "janela")

    def test_edicao_dupla(self):
        self.assertEqual(self.c.corrigir("cassaa"), "casa")

    def test_capitalizacao(self):
        self.assertEqual(self.c.corrigir("Casaa"), "Casa")

    def test_sem_candidato(self):
        self.assertEqual(self.c.corrigir("xyzxyzxyz"), "xyzxyzxyz")
        self.assertEqual(self.c.corrigir(""), "")

    def test_frequencia_desempata(self):
        c = Corretor({"bala": 1, "bola": 9})
        self.assertEqual(c.corrigir("bxla"), "bola")

    def test_de_texto(self):
        c = Corretor.de_texto("o sol brilha e o sol aquece")
        self.assertEqual(c.corrigir("soll"), "sol")


if __name__ == "__main__":
    unittest.main()
