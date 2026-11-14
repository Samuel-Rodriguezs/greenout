import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from crip_blockchain import Blockchain


class TestBlockchain(unittest.TestCase):
    def test_pow(self):
        bc = Blockchain(2)
        b = bc.adicionar("alice->bob 5")
        self.assertTrue(b.hash.startswith("00"))
        self.assertEqual(b.anterior, bc.blocos[0].hash)
        self.assertEqual(b.hash, b.calcular_hash())

    def test_valida(self):
        bc = Blockchain(1)
        for i in range(4):
            bc.adicionar(f"tx{i}")
        self.assertTrue(bc.valida())
        self.assertEqual(len(bc.blocos), 5)

    def test_adulteracao_dados(self):
        bc = Blockchain(1)
        bc.adicionar("a")
        bc.adicionar("b")
        bc.blocos[1].dados = "fraude"
        self.assertFalse(bc.valida())

    def test_adulteracao_reminerada_quebra_elo(self):
        bc = Blockchain(1)
        bc.adicionar("a")
        bc.adicionar("b")
        bc.blocos[1].dados = "fraude"
        bc.blocos[1].minerar(1)
        self.assertFalse(bc.valida())  # bloco 2 aponta para o hash antigo

    def test_dificuldade_zero_e_negativa(self):
        self.assertTrue(Blockchain(0).valida())
        with self.assertRaises(ValueError):
            Blockchain(-1)


if __name__ == "__main__":
    unittest.main()
