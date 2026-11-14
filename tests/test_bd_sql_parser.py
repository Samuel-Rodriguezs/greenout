import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bd_sql_parser import (Apagar, Atualizar, Binario, Chamada, Coluna, CriarTabela,
                           EhNulo, EmLista, Entre, ErroSQL, Inserir, Literal, Selecionar,
                           Unario, contem_agregado, parse, tokenizar)


class TestTokenizer(unittest.TestCase):
    def test_tokens_basicos(self):
        t = tokenizar("SELECT a, 1.5 FROM t WHERE x <> 'it''s'")
        tipos = [(x.tipo, x.valor) for x in t]
        self.assertIn(("NUM", 1.5), tipos)
        self.assertIn(("STR", "it's"), tipos)
        self.assertIn(("OP", "<>"), tipos)
        self.assertEqual(t[-1].tipo, "FIM")

    def test_nao_igual_vira_diferente(self):
        self.assertEqual(tokenizar("a != b")[1].valor, "<>")

    def test_palavras_chave_sem_caixa(self):
        self.assertEqual(tokenizar("select")[0].tipo, "KW")

    def test_comentario(self):
        self.assertEqual(len(tokenizar("-- nada\nSELECT")), 2)

    def test_caractere_invalido(self):
        with self.assertRaises(ErroSQL):
            tokenizar("SELECT @")

    def test_texto_nao_terminado(self):
        with self.assertRaises(ErroSQL):
            tokenizar("SELECT 'abc")


class TestParser(unittest.TestCase):
    def test_create(self):
        c = parse("CREATE TABLE usuarios (id INT PRIMARY KEY, nome VARCHAR(30), nota REAL);")
        self.assertIsInstance(c, CriarTabela)
        self.assertEqual(c.colunas, [("id", "INT", True), ("nome", "VARCHAR", False), ("nota", "REAL", False)])

    def test_create_invalidos(self):
        for sql in ("CREATE TABLE t (a INT, a TEXT)",
                    "CREATE TABLE t (a INT PRIMARY KEY, b INT PRIMARY KEY)",
                    "CREATE TABLE t (a BLOB)",
                    "CREATE TABLE t ()"):
            with self.assertRaises(ErroSQL, msg=sql):
                parse(sql)

    def test_insert_multiplas_linhas(self):
        c = parse("INSERT INTO t (a, b) VALUES (1, 'x'), (2, NULL)")
        self.assertIsInstance(c, Inserir)
        self.assertEqual(c.colunas, ["a", "b"])
        self.assertEqual(c.linhas[1], [Literal(2), Literal(None)])

    def test_insert_sem_colunas_e_negativo(self):
        c = parse("INSERT INTO t VALUES (-3, -1.5)")
        self.assertEqual(c.linhas[0], [Literal(-3), Literal(-1.5)])
        self.assertIsNone(c.colunas)

    def test_insert_erros(self):
        for sql in ("INSERT INTO t (a, b) VALUES (1)",
                    "INSERT INTO t VALUES (1), (1, 2)",
                    "INSERT INTO t VALUES"):
            with self.assertRaises(ErroSQL, msg=sql):
                parse(sql)

    def test_select_completo(self):
        s = parse("""SELECT DISTINCT u.nome AS n, COUNT(*) total FROM usuarios u
                     JOIN pedidos p ON p.uid = u.id WHERE u.idade >= 18 AND p.valor > 10
                     GROUP BY u.nome HAVING COUNT(*) > 1 ORDER BY total DESC, n LIMIT 5""")
        self.assertIsInstance(s, Selecionar)
        self.assertTrue(s.distinto)
        self.assertEqual(s.alias, "u")
        self.assertEqual(s.itens[0].alias, "n")
        self.assertEqual(s.itens[0].expr, Coluna("nome", "u"))
        self.assertEqual(s.itens[1].expr, Chamada("COUNT", (), True))
        self.assertEqual(s.juncoes[0].tabela, "pedidos")
        self.assertEqual(s.limite, 5)
        self.assertEqual([d for _, d in s.order_by], [True, False])
        self.assertIsNotNone(s.having)

    def test_select_estrela(self):
        s = parse("SELECT * FROM t")
        self.assertIsNone(s.itens[0].expr)

    def test_precedencia(self):
        s = parse("SELECT * FROM t WHERE a = 1 OR b = 2 AND c = 3")
        self.assertEqual(s.where.op, "OR")
        self.assertEqual(s.where.dir.op, "AND")
        s = parse("SELECT 1 + 2 * 3 FROM t")
        e = s.itens[0].expr
        self.assertEqual((e.op, e.dir.op), ("+", "*"))
        s = parse("SELECT (1 + 2) * 3 FROM t")
        self.assertEqual(s.itens[0].expr.op, "*")

    def test_predicados_especiais(self):
        s = parse("SELECT * FROM t WHERE a IS NOT NULL AND b NOT IN (1, 2) AND c BETWEEN 1 AND 5 AND d NOT LIKE 'x%'")
        partes = []
        e = s.where
        while isinstance(e, Binario) and e.op == "AND":
            partes.append(e.dir)
            e = e.esq
        partes.append(e)
        tipos = {type(p) for p in partes}
        self.assertEqual(tipos, {EhNulo, EmLista, Entre, Unario})
        em = next(p for p in partes if isinstance(p, EmLista))
        self.assertTrue(em.negado)

    def test_update_e_delete(self):
        u = parse("UPDATE t SET a = a + 1, b = 'z' WHERE id = 3")
        self.assertIsInstance(u, Atualizar)
        self.assertEqual([c for c, _ in u.atribuicoes], ["a", "b"])
        d = parse("DELETE FROM t")
        self.assertIsInstance(d, Apagar)
        self.assertIsNone(d.where)

    def test_erros_de_sintaxe(self):
        for sql in ("", "SELECT", "SELECT a FROM", "SELECT a FROM t WHERE",
                    "SELECT a FROM t extra junk", "DROP TABLE t",
                    "SELECT a FROM t LIMIT 1.5", "SELECT SUM(*) FROM t",
                    "SELECT SUM(a, b) FROM t", "UPDATE t SET WHERE a = 1",
                    "SELECT (a FROM t"):
            with self.assertRaises(ErroSQL, msg=sql):
                parse(sql)

    def test_mensagem_de_erro_tem_posicao(self):
        with self.assertRaises(ErroSQL) as ctx:
            parse("SELECT a FROM")
        self.assertIn("posição", str(ctx.exception))

    def test_contem_agregado(self):
        s = parse("SELECT SUM(a) + 1, b FROM t")
        self.assertTrue(contem_agregado(s.itens[0].expr))
        self.assertFalse(contem_agregado(s.itens[1].expr))


if __name__ == "__main__":
    unittest.main()
