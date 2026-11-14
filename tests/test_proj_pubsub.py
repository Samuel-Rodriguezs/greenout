import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from proj_pubsub import BarramentoEventos


class TestPubSub(unittest.TestCase):
    def setUp(self):
        self.b = BarramentoEventos()
        self.rec = []

    def handler(self, topico, dados):
        self.rec.append((topico, dados))

    def test_topico_exato(self):
        self.b.assinar("pedido.criado", self.handler)
        self.assertEqual(self.b.publicar("pedido.criado", 1), 1)
        self.assertEqual(self.b.publicar("pedido.pago", 2), 0)
        self.assertEqual(self.rec, [("pedido.criado", 1)])

    def test_wildcard(self):
        self.b.assinar("pedido.*", self.handler)
        self.b.publicar("pedido.criado")
        self.b.publicar("pedido.pago")
        self.b.publicar("usuario.novo")
        self.assertEqual(len(self.rec), 2)

    def test_multiplos_assinantes(self):
        outros = []
        self.b.assinar("x", self.handler)
        self.b.assinar("x", lambda t, d: outros.append(d))
        self.assertEqual(self.b.publicar("x", 7), 2)
        self.assertEqual(outros, [7])

    def test_cancelar(self):
        id_ = self.b.assinar("x", self.handler)
        self.b.cancelar(id_)
        self.assertEqual(self.b.publicar("x"), 0)
        with self.assertRaises(KeyError):
            self.b.cancelar(id_)

    def test_erro_em_handler_isolado(self):
        def ruim(t, d):
            raise RuntimeError("falha")

        self.b.assinar("x", ruim)
        self.b.assinar("x", self.handler)
        self.assertEqual(self.b.publicar("x", 1), 1)
        self.assertEqual(len(self.rec), 1)
        self.assertIsInstance(self.b.erros[0][1], RuntimeError)

    def test_validacoes(self):
        with self.assertRaises(ValueError):
            self.b.assinar("", self.handler)
        with self.assertRaises(TypeError):
            self.b.assinar("x", 5)


if __name__ == "__main__":
    unittest.main()
