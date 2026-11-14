import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from web_orm import Modelo, RegistroNaoEncontrado


class Usuario(Modelo):
    tabela = "usuarios"
    colunas = {"nome": "str", "idade": "int", "ativo": "bool"}


class TestWebOrm(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        Usuario.vincular(self.con)
        Usuario.criar_tabela()

    def tearDown(self):
        self.con.close()
        Usuario.conexao = None

    def test_criar_e_buscar(self):
        u = Usuario.criar(nome="Ana", idade=30, ativo=True)
        self.assertEqual(u.id, 1)
        b = Usuario.buscar(1)
        self.assertEqual(b.para_dict(), {"id": 1, "nome": "Ana", "idade": 30, "ativo": True})

    def test_atualizar(self):
        u = Usuario.criar(nome="Ana", idade=30, ativo=False)
        u.idade = 31
        u.salvar()
        self.assertEqual(Usuario.buscar(u.id).idade, 31)
        self.assertEqual(Usuario.contar(), 1)

    def test_deletar(self):
        u = Usuario.criar(nome="Ana", idade=1, ativo=True)
        uid = u.id
        u.deletar()
        self.assertIsNone(u.id)
        with self.assertRaises(RegistroNaoEncontrado):
            Usuario.buscar(uid)
        with self.assertRaises(ValueError):
            u.deletar()

    def test_listar_filtros_e_ordem(self):
        Usuario.criar(nome="B", idade=20, ativo=True)
        Usuario.criar(nome="A", idade=20, ativo=False)
        Usuario.criar(nome="C", idade=None, ativo=True)
        self.assertEqual([u.nome for u in Usuario.listar(ordem="nome")], ["A", "B", "C"])
        self.assertEqual([u.nome for u in Usuario.listar(ordem="-nome", limite=2)], ["C", "B"])
        self.assertEqual(len(Usuario.listar(idade=20)), 2)
        self.assertEqual([u.nome for u in Usuario.listar(idade=None)], ["C"])

    def test_erros(self):
        with self.assertRaises(RegistroNaoEncontrado):
            Usuario.buscar(99)
        with self.assertRaises(TypeError):
            Usuario(xyz=1)
        with self.assertRaises(ValueError):
            Usuario.listar(**{"nome; DROP": 1})
        with self.assertRaises(ValueError):
            Usuario.listar(ordem="x; DROP")
        fantasma = Usuario(id=500, nome="x", idade=1, ativo=True)
        with self.assertRaises(RegistroNaoEncontrado):
            fantasma.salvar()

    def test_sem_conexao_e_definicao_invalida(self):
        Usuario.conexao = None
        with self.assertRaises(RuntimeError):
            Usuario.contar()

        class Ruim(Modelo):
            tabela = "x y"
            colunas = {}

        Ruim.vincular(self.con)
        with self.assertRaises(ValueError):
            Ruim.criar_tabela()

        class RuimTipo(Modelo):
            tabela = "t"
            colunas = {"a": "date"}

        RuimTipo.vincular(self.con)
        with self.assertRaises(ValueError):
            RuimTipo.criar_tabela()
        Ruim.conexao = RuimTipo.conexao = None


if __name__ == "__main__":
    unittest.main()
