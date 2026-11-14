import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_elevator import Elevador


class TestKataElevator(unittest.TestCase):
    def test_estado_inicial(self):
        e = Elevador(5, 2)
        self.assertEqual(e.andar, 2)
        self.assertTrue(e.ocioso())
        self.assertFalse(e.porta_aberta)

    def test_sem_chamadas_nao_se_move(self):
        e = Elevador()
        e.passo()
        self.assertEqual(e.andar, 0)

    def test_sobe_ate_o_andar(self):
        e = Elevador(10)
        e.chamar(3)
        self.assertEqual(e.executar_ate_ocioso(), [0, 1, 2, 3])
        self.assertTrue(e.porta_aberta)
        self.assertEqual(e.direcao, 0)

    def test_desce_ate_o_andar(self):
        e = Elevador(10, 5)
        e.chamar(2)
        self.assertEqual(e.executar_ate_ocioso(), [5, 4, 3, 2])

    def test_paradas_no_caminho(self):
        e = Elevador(10)
        e.chamar(5)
        e.chamar(2)
        e.passo()
        e.passo()
        self.assertEqual(e.andar, 2)
        self.assertTrue(e.porta_aberta)
        e.passo()
        self.assertFalse(e.porta_aberta)
        self.assertEqual(e.andar, 3)

    def test_atende_subindo_depois_desce(self):
        e = Elevador(10, 5)
        e.chamar(8)
        e.chamar(1)
        self.assertEqual(e.executar_ate_ocioso(), [5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 1])

    def test_chamada_no_mesmo_andar_so_abre_porta(self):
        e = Elevador(5, 1)
        e.chamar(1)
        self.assertTrue(e.porta_aberta)
        self.assertTrue(e.ocioso())
        e.passo()
        self.assertFalse(e.porta_aberta)

    def test_nova_chamada_durante_o_trajeto(self):
        e = Elevador(10)
        e.chamar(6)
        for _ in range(2):
            e.passo()
        e.chamar(4)
        e.executar_ate_ocioso()
        self.assertEqual(e.historico, [0, 1, 2, 3, 4, 5, 6])

    def test_chamada_repetida_conta_uma_vez(self):
        e = Elevador(10)
        e.chamar(2)
        e.chamar(2)
        self.assertEqual(e.paradas, {2})

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            Elevador(1)
        with self.assertRaises(ValueError):
            Elevador(5, 5)
        with self.assertRaises(ValueError):
            Elevador(5).chamar(5)
        with self.assertRaises(ValueError):
            Elevador(5).chamar(-1)


if __name__ == "__main__":
    unittest.main()
