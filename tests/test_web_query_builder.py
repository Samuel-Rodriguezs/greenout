import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from web_query_builder import Consulta, atualizar, inserir, remover


class TestWebQueryBuilder(unittest.TestCase):
    def test_select_completo(self):
        sql, p = (Consulta("usuarios").selecionar("id", "nome")
                  .onde("idade", ">=", 18).ou_onde("vip", 1)
                  .ordenar("nome").ordenar("id", True).limite(10, 20).construir())
        self.assertEqual(sql, "SELECT id, nome FROM usuarios WHERE idade >= ? OR vip = ? "
                              "ORDER BY nome ASC, id DESC LIMIT 10 OFFSET 20")
        self.assertEqual(p, [18, 1])

    def test_select_simples(self):
        self.assertEqual(Consulta("t").construir(), ("SELECT * FROM t", []))

    def test_in_e_null(self):
        sql, p = Consulta("t").onde("a", "IN", [1, 2]).onde("b", None).onde("c", "!=", None).construir()
        self.assertEqual(sql, "SELECT * FROM t WHERE a IN (?, ?) AND b IS NULL AND c IS NOT NULL")
        self.assertEqual(p, [1, 2])
        self.assertIn("1 = 0", Consulta("t").onde("a", "IN", []).construir()[0])

    def test_join_group_distinct(self):
        sql, _ = (Consulta("a").distinto().selecionar("a.x").juntar("b", "a.id", "b.a_id", "left")
                  .agrupar_por("a.x").construir())
        self.assertEqual(sql, "SELECT DISTINCT a.x FROM a LEFT JOIN b ON a.id = b.a_id GROUP BY a.x")

    def test_injecao_bloqueada(self):
        with self.assertRaises(ValueError):
            Consulta("t; DROP TABLE t")
        with self.assertRaises(ValueError):
            Consulta("t").onde("a OR 1=1 --", 1)
        with self.assertRaises(ValueError):
            Consulta("t").onde("a", "; DROP", 1)
        with self.assertRaises(ValueError):
            Consulta("t").onde("a", ">", None)
        with self.assertRaises(ValueError):
            Consulta("t").limite(-1)
        with self.assertRaises(ValueError):
            Consulta("t").juntar("b", "a.x", "b.y", "cross")

    def test_valor_malicioso_e_parametro(self):
        sql, p = Consulta("t").onde("nome", "x'; DROP TABLE t; --").construir()
        self.assertNotIn("DROP", sql)
        self.assertEqual(p, ["x'; DROP TABLE t; --"])

    def test_dml(self):
        self.assertEqual(inserir("t", {"a": 1, "b": 2}),
                         ("INSERT INTO t (a, b) VALUES (?, ?)", [1, 2]))
        self.assertEqual(atualizar("t", {"a": 1}, {"id": 5}),
                         ("UPDATE t SET a = ? WHERE id = ?", [1, 5]))
        self.assertEqual(remover("t", {"id": 5}), ("DELETE FROM t WHERE id = ?", [5]))

    def test_dml_invalido(self):
        with self.assertRaises(ValueError):
            inserir("t", {})
        with self.assertRaises(ValueError):
            atualizar("t", {"a": 1}, {})
        with self.assertRaises(ValueError):
            atualizar("t", {}, {"id": 1})
        with self.assertRaises(ValueError):
            remover("t", {})

    def test_executa_no_sqlite(self):
        con = sqlite3.connect(":memory:")
        self.addCleanup(con.close)
        con.execute("CREATE TABLE u (id INTEGER PRIMARY KEY, nome TEXT, idade INT)")
        con.execute(*inserir("u", {"nome": "Ana", "idade": 30}))
        con.execute(*inserir("u", {"nome": "Beto", "idade": 15}))
        con.execute(*atualizar("u", {"idade": 16}, {"nome": "Beto"}))
        linhas = con.execute(*Consulta("u").onde("idade", ">", 20).construir()).fetchall()
        self.assertEqual(linhas, [(1, "Ana", 30)])
        con.execute(*remover("u", {"nome": "Ana"}))
        self.assertEqual(con.execute("SELECT COUNT(*) FROM u").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
