import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bd_catalogo import Catalogo, ErroCatalogo
from bd_sql_parser import parse


class TestCatalogo(unittest.TestCase):
    def setUp(self):
        self.c = Catalogo()
        self.c.criar_de_ast(parse("CREATE TABLE Usuarios (Id INT PRIMARY KEY, nome VARCHAR(20), nota FLOAT)"))
        self.c.criar_tabela("pedidos", [("id", "integer", True), ("uid", "INT", False)])

    def test_normaliza_nomes_e_tipos(self):
        t = self.c.tabela("USUARIOS")
        self.assertEqual(t.esquema(), [("id", "INT"), ("nome", "TEXT"), ("nota", "REAL")])
        self.assertEqual(t.chave_primaria, "id")

    def test_tabela_duplicada_e_inexistente(self):
        with self.assertRaises(ErroCatalogo):
            self.c.criar_tabela("usuarios", [("a", "INT", False)])
        with self.assertRaises(ErroCatalogo):
            self.c.tabela("nada")

    def test_definicoes_invalidas(self):
        with self.assertRaises(ErroCatalogo):
            self.c.criar_tabela("x", [])
        with self.assertRaises(ErroCatalogo):
            self.c.criar_tabela("x", [("a", "BLOB", False)])
        with self.assertRaises(ErroCatalogo):
            self.c.criar_tabela("x", [("a", "INT", False), ("A", "INT", False)])
        with self.assertRaises(ErroCatalogo):
            self.c.criar_tabela("x", [("a", "INT", True), ("b", "INT", True)])
        self.assertNotIn("x", self.c.tabelas)

    def test_indice_automatico_da_pk(self):
        t = self.c.tabela("usuarios")
        self.assertEqual(t.indice_da_coluna("ID").nome, "pk_usuarios")
        self.assertTrue(t.indice_da_coluna("id").unico)
        with self.assertRaises(ErroCatalogo):
            self.c.remover_indice("pk_usuarios")

    def test_criar_e_remover_indice(self):
        self.c.criar_indice("idx_nome", "usuarios", "nome")
        self.assertIsNotNone(self.c.tabela("usuarios").indice_da_coluna("nome"))
        with self.assertRaises(ErroCatalogo):
            self.c.criar_indice("idx_nome", "pedidos", "uid")  # nome global
        with self.assertRaises(ErroCatalogo):
            self.c.criar_indice("outro", "usuarios", "nome")   # coluna já indexada
        with self.assertRaises(ErroCatalogo):
            self.c.criar_indice("i3", "usuarios", "inexistente")
        self.c.remover_indice("IDX_NOME")
        self.assertIsNone(self.c.tabela("usuarios").indice_da_coluna("nome"))
        with self.assertRaises(ErroCatalogo):
            self.c.remover_indice("idx_nome")

    def test_resolver_coluna(self):
        self.assertEqual(self.c.resolver_coluna("nome", ["usuarios", "pedidos"]), ("usuarios", 1))
        self.assertEqual(self.c.resolver_coluna("uid", ["usuarios", "pedidos"]), ("pedidos", 1))
        with self.assertRaises(ErroCatalogo):
            self.c.resolver_coluna("id", ["usuarios", "pedidos"])  # ambígua
        with self.assertRaises(ErroCatalogo):
            self.c.resolver_coluna("zzz", ["usuarios"])

    def test_remover_tabela(self):
        self.c.remover_tabela("pedidos")
        with self.assertRaises(ErroCatalogo):
            self.c.tabela("pedidos")
        with self.assertRaises(ErroCatalogo):
            self.c.remover_tabela("pedidos")

    def test_persistencia_ida_e_volta(self):
        self.c.criar_indice("idx_nome", "usuarios", "nome")
        self.c.tabela("usuarios").n_linhas = 123
        with tempfile.TemporaryDirectory() as d:
            caminho = os.path.join(d, "catalogo.json")
            self.c.salvar(caminho)
            self.assertFalse(os.path.exists(caminho + ".tmp"))
            outro = Catalogo.carregar(caminho)
        self.assertEqual(outro.para_dict(), self.c.para_dict())
        self.assertEqual(outro.tabela("usuarios").n_linhas, 123)

    def test_carregar_corrompido_ou_versao_errada(self):
        with tempfile.TemporaryDirectory() as d:
            caminho = os.path.join(d, "c.json")
            with open(caminho, "w") as f:
                f.write('{"versao": 1, "tabe')
            with self.assertRaises(ErroCatalogo):
                Catalogo.carregar(caminho)
            with open(caminho, "w") as f:
                json.dump({"versao": 99, "tabelas": []}, f)
            with self.assertRaises(ErroCatalogo):
                Catalogo.carregar(caminho)
            with open(caminho, "w") as f:
                json.dump({"versao": 1, "tabelas": [{"nome": "t"}]}, f)
            with self.assertRaises(ErroCatalogo):
                Catalogo.carregar(caminho)


if __name__ == "__main__":
    unittest.main()
