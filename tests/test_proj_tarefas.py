import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from proj_tarefas import GerenciadorTarefas


class TestTarefas(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.caminho = Path(self.dir.name) / "t.json"

    def tearDown(self):
        self.dir.cleanup()

    def test_adicionar_e_persistir(self):
        g = GerenciadorTarefas(self.caminho)
        g.adicionar("estudar")
        g.adicionar("treinar")
        g2 = GerenciadorTarefas(self.caminho)
        self.assertEqual([t.titulo for t in g2.tarefas], ["estudar", "treinar"])

    def test_concluir_e_pendentes(self):
        g = GerenciadorTarefas(self.caminho)
        a = g.adicionar("a")
        g.adicionar("b")
        g.concluir(a.id)
        self.assertEqual([t.titulo for t in g.pendentes()], ["b"])
        self.assertTrue(GerenciadorTarefas(self.caminho).tarefas[0].concluida)

    def test_remover_e_novo_id(self):
        g = GerenciadorTarefas(self.caminho)
        g.adicionar("a")
        b = g.adicionar("b")
        g.remover(b.id)
        self.assertEqual(g.adicionar("c").id, 2)

    def test_erros(self):
        g = GerenciadorTarefas(self.caminho)
        with self.assertRaises(ValueError):
            g.adicionar("   ")
        with self.assertRaises(KeyError):
            g.concluir(99)
        with self.assertRaises(KeyError):
            g.remover(99)


if __name__ == "__main__":
    unittest.main()
