import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_eventos import BarramentoEventos


class TestEventos(unittest.TestCase):
    def test_prioridade(self):
        b = BarramentoEventos()
        log = []
        b.assinar("x", lambda d: log.append("baixa"), 0)
        b.assinar("x", lambda d: log.append("alta"), 5)
        b.assinar("x", lambda d: log.append("baixa2"), 0)
        self.assertEqual(b.publicar("x"), 3)
        self.assertEqual(log, ["alta", "baixa", "baixa2"])

    def test_uma_vez(self):
        b = BarramentoEventos()
        n = []
        b.assinar("x", n.append, uma_vez=True)
        b.publicar("x", 1)
        b.publicar("x", 2)
        self.assertEqual(n, [1])
        self.assertEqual(b.quantidade("x"), 0)

    def test_cancelar(self):
        b = BarramentoEventos()
        n = []
        c = b.assinar("x", n.append)
        c()
        c()
        self.assertEqual(b.publicar("x", 1), 0)
        self.assertEqual(n, [])

    def test_cancelar_durante_publicacao(self):
        b = BarramentoEventos()
        log = []
        cancela = []
        b.assinar("x", lambda d: (log.append("a"), cancela[0]()), 1)
        cancela.append(b.assinar("x", lambda d: log.append("b"), 0))
        self.assertEqual(b.publicar("x"), 1)
        self.assertEqual(log, ["a"])

    def test_fila_com_reentrada(self):
        b = BarramentoEventos()
        log = []
        b.assinar("a", lambda d: (log.append(("a", d)), b.enfileirar("b", d + 1)))
        b.assinar("b", lambda d: log.append(("b", d)))
        b.enfileirar("a", 1)
        self.assertEqual(b.despachar(), 2)
        self.assertEqual(log, [("a", 1), ("b", 2)])

    def test_topico_sem_ouvinte(self):
        self.assertEqual(BarramentoEventos().publicar("nada"), 0)


if __name__ == "__main__":
    unittest.main()
