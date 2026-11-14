import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_sistemas import Agendador


class TestAgendador(unittest.TestCase):
    def test_ordem_por_prioridade_e_registro(self):
        a = Agendador()
        a.registrar("fisica", lambda w, dt: None, 10)
        a.registrar("input", lambda w, dt: None, 0)
        a.registrar("ia", lambda w, dt: None, 10)
        self.assertEqual(a.ordem(), ["input", "fisica", "ia"])

    def test_executa_com_mundo_e_dt(self):
        log = []
        a = Agendador()
        a.registrar("b", lambda w, dt: log.append(("b", w, dt)), 2)
        a.registrar("a", lambda w, dt: log.append(("a", w, dt)), 1)
        self.assertEqual(a.executar("W", 0.5), ["a", "b"])
        self.assertEqual(log, [("a", "W", 0.5), ("b", "W", 0.5)])

    def test_desabilitar(self):
        log = []
        a = Agendador()
        a.registrar("x", lambda w, dt: log.append("x"))
        a.habilitar("x", False)
        self.assertEqual(a.executar(None, 1), [])
        a.habilitar("x", True)
        a.executar(None, 1)
        self.assertEqual(log, ["x"])

    def test_remover_e_erros(self):
        a = Agendador()
        a.registrar("x", lambda w, dt: None)
        with self.assertRaises(ValueError):
            a.registrar("x", lambda w, dt: None)
        a.remover("x")
        with self.assertRaises(KeyError):
            a.remover("x")
        with self.assertRaises(KeyError):
            a.habilitar("x", True)

    def test_remover_durante_execucao(self):
        a = Agendador()
        a.registrar("a", lambda w, dt: a.remover("b"), 0)
        a.registrar("b", lambda w, dt: None, 1)
        self.assertEqual(a.executar(None, 0), ["a", "b"])
        self.assertEqual(a.ordem(), ["a"])


if __name__ == "__main__":
    unittest.main()
