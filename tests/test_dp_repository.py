import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_repository import Cliente, RepositorioMemoria, RepositorioSqlite


class ContratoRepositorio:
    def criar(self):
        raise NotImplementedError

    def test_salvar_atribui_id(self):
        r = self.criar()
        c = r.salvar(Cliente(None, "Ana", "a@x"))
        self.assertEqual(c.id, 1)
        self.assertEqual(r.obter(1), c)

    def test_atualizar(self):
        r = self.criar()
        c = r.salvar(Cliente(None, "Ana", "a@x"))
        r.salvar(Cliente(c.id, "Ana Maria", "a@x"))
        self.assertEqual(r.obter(c.id).nome, "Ana Maria")
        self.assertEqual(len(r.listar()), 1)

    def test_remover(self):
        r = self.criar()
        c = r.salvar(Cliente(None, "Ana", "a@x"))
        self.assertTrue(r.remover(c.id))
        self.assertFalse(r.remover(c.id))
        self.assertIsNone(r.obter(c.id))

    def test_buscar_por_email(self):
        r = self.criar()
        r.salvar(Cliente(None, "Ana", "a@x"))
        r.salvar(Cliente(None, "Bia", "b@x"))
        self.assertEqual(r.buscar_por_email("b@x").nome, "Bia")
        self.assertIsNone(r.buscar_por_email("z@x"))


class TestMemoria(ContratoRepositorio, unittest.TestCase):
    def criar(self):
        return RepositorioMemoria()


class TestSqlite(ContratoRepositorio, unittest.TestCase):
    def criar(self):
        return RepositorioSqlite(sqlite3.connect(":memory:"))


if __name__ == "__main__":
    unittest.main()
