import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sim_elevador import Elevador


class TestElevador(unittest.TestCase):
    def test_viagem_simples(self):
        e = Elevador(10)
        e.chamar(0, 5)
        passos = e.executar_ate_ocioso()
        self.assertEqual(e.entregues, 1)
        self.assertEqual(e.andar, 5)
        self.assertEqual(passos, 6)  # 5 deslocamentos + 1 passo para desembarcar

    def test_busca_passageiro_acima(self):
        e = Elevador(10)
        e.chamar(4, 2)
        e.executar_ate_ocioso()
        self.assertEqual(e.entregues, 1)
        self.assertEqual(e.andar, 2)

    def test_scan_atende_no_caminho(self):
        e = Elevador(10)
        e.chamar(0, 8)
        e.chamar(3, 6)
        e.passo()  # embarca o primeiro e sobe
        n = e.executar_ate_ocioso()
        self.assertEqual(e.entregues, 2)
        self.assertEqual(e.andar, 8)
        self.assertEqual(n, 8)  # sobe sem voltar e desembarca no 8

    def test_inverte_direcao(self):
        e = Elevador(10, andar_inicial=5)
        e.chamar(2, 0)
        e.chamar(7, 9)
        e.executar_ate_ocioso()
        self.assertEqual(e.entregues, 2)

    def test_capacidade(self):
        e = Elevador(5, capacidade=2)
        for _ in range(3):
            e.chamar(0, 4)
        e.passo()
        self.assertEqual(len(e.dentro), 2)
        self.assertEqual(len(e.espera), 1)
        e.executar_ate_ocioso()
        self.assertEqual(e.entregues, 3)

    def test_ocioso_nao_move(self):
        e = Elevador(5, andar_inicial=2)
        e.passo()
        self.assertEqual(e.andar, 2)
        self.assertTrue(e.ocioso)

    def test_validacoes(self):
        e = Elevador(5)
        with self.assertRaises(ValueError):
            e.chamar(0, 5)
        with self.assertRaises(ValueError):
            e.chamar(2, 2)
        with self.assertRaises(ValueError):
            Elevador(5, andar_inicial=7)


if __name__ == "__main__":
    unittest.main()
