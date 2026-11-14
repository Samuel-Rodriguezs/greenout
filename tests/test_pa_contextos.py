import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from pa_contextos import Transacao, diretorio_atual, suprimir_registrando


class TestContextos(unittest.TestCase):
    def test_diretorio_restaurado(self):
        antes = os.getcwd()
        with tempfile.TemporaryDirectory() as d:
            with diretorio_atual(d) as atual:
                self.assertEqual(os.path.realpath(atual), os.path.realpath(d))
            self.assertEqual(os.getcwd(), antes)

    def test_diretorio_restaurado_com_erro(self):
        antes = os.getcwd()
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(RuntimeError):
                with diretorio_atual(d):
                    raise RuntimeError()
        self.assertEqual(os.getcwd(), antes)

    def test_diretorio_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            with diretorio_atual("/caminho/que/nao/existe"):
                pass

    def test_transacao_commit(self):
        d = {"a": 1}
        with Transacao(d) as t:
            t["b"] = 2
        self.assertEqual(d, {"a": 1, "b": 2})

    def test_transacao_rollback(self):
        d = {"a": 1}
        with self.assertRaises(ValueError):
            with Transacao(d) as t:
                t["a"] = 99
                del t["a"]
                t["c"] = 3
                raise ValueError()
        self.assertEqual(d, {"a": 1})

    def test_suprimir_registrando(self):
        erros = []
        with suprimir_registrando(erros, KeyError, ValueError):
            raise ValueError("x")
        self.assertEqual(len(erros), 1)
        with self.assertRaises(TypeError):
            with suprimir_registrando(erros, KeyError):
                raise TypeError()
        self.assertEqual(len(erros), 1)


if __name__ == "__main__":
    unittest.main()
