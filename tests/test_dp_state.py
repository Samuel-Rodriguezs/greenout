import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_state import EstadoInvalido, Pedido


class TestState(unittest.TestCase):
    def test_fluxo_feliz(self):
        p = Pedido()
        self.assertEqual(p.situacao, "criado")
        p.pagar()
        p.enviar()
        p.entregar()
        self.assertEqual(p.situacao, "entregue")

    def test_transicao_invalida(self):
        p = Pedido()
        with self.assertRaises(EstadoInvalido):
            p.enviar()
        self.assertEqual(p.situacao, "criado")

    def test_cancelamento(self):
        p = Pedido()
        p.pagar()
        p.cancelar()
        self.assertEqual(p.situacao, "cancelado")
        with self.assertRaises(EstadoInvalido):
            p.pagar()

    def test_nao_cancela_depois_de_enviado(self):
        p = Pedido()
        p.pagar()
        p.enviar()
        with self.assertRaises(EstadoInvalido):
            p.cancelar()

    def test_final_entregue(self):
        p = Pedido()
        p.pagar(); p.enviar(); p.entregar()
        for op in (p.pagar, p.enviar, p.entregar, p.cancelar):
            with self.assertRaises(EstadoInvalido):
                op()


if __name__ == "__main__":
    unittest.main()
