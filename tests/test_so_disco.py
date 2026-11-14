import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from so_disco import escalonar

FILA = [98, 183, 37, 122, 14, 124, 65, 67]
CABECOTE = 53


class TestDisco(unittest.TestCase):
    def test_fcfs(self):
        r = escalonar(FILA, CABECOTE, "fcfs")
        self.assertEqual(r.atendimento, tuple(FILA))
        self.assertEqual(r.movimento, 640)

    def test_sstf(self):
        r = escalonar(FILA, CABECOTE, "sstf")
        self.assertEqual(r.atendimento, (65, 67, 37, 14, 98, 122, 124, 183))
        self.assertEqual(r.movimento, 236)

    def test_scan_descendo(self):
        r = escalonar(FILA, CABECOTE, "scan", direcao="baixo")
        self.assertEqual(r.atendimento, (37, 14, 65, 67, 98, 122, 124, 183))
        self.assertEqual(r.percurso[:4], (53, 37, 14, 0))
        self.assertEqual(r.movimento, 236)

    def test_scan_subindo_vai_ate_a_borda(self):
        r = escalonar(FILA, CABECOTE, "scan")
        self.assertEqual(r.atendimento, (65, 67, 98, 122, 124, 183, 37, 14))
        self.assertIn(199, r.percurso)
        self.assertEqual(r.movimento, 146 + 185)

    def test_cscan(self):
        r = escalonar(FILA, CABECOTE, "cscan")
        self.assertEqual(r.atendimento, (65, 67, 98, 122, 124, 183, 14, 37))
        self.assertEqual(r.percurso, (53, 65, 67, 98, 122, 124, 183, 199, 0, 14, 37))
        self.assertEqual(r.movimento, 146 + 199 + 37)

    def test_look_e_clook(self):
        self.assertEqual(escalonar(FILA, CABECOTE, "look").movimento, 130 + 169)
        r = escalonar(FILA, CABECOTE, "clook")
        self.assertEqual(r.atendimento, (65, 67, 98, 122, 124, 183, 14, 37))
        self.assertEqual(r.movimento, 130 + 169 + 23)

    def test_sstf_empate_vai_para_o_primeiro_da_fila(self):
        r = escalonar([60, 40], 50, "sstf")
        self.assertEqual(r.atendimento, (60, 40))

    def test_pedido_na_posicao_atual(self):
        r = escalonar([50, 70], 50, "scan")
        self.assertEqual(r.atendimento, (50, 70))

    def test_sem_pedidos(self):
        for alg in ("fcfs", "sstf", "scan", "cscan", "look", "clook"):
            self.assertEqual(escalonar([], 10, alg).movimento, 0)

    def test_scan_e_menor_que_fcfs_no_exemplo(self):
        self.assertLess(
            escalonar(FILA, CABECOTE, "scan", "baixo").movimento,
            escalonar(FILA, CABECOTE, "fcfs").movimento,
        )

    def test_validacao(self):
        with self.assertRaises(ValueError):
            escalonar([1], 0, "elevador")
        with self.assertRaises(ValueError):
            escalonar([200], 0, "fcfs")
        with self.assertRaises(ValueError):
            escalonar([1], 0, "scan", direcao="lado")


if __name__ == "__main__":
    unittest.main()
