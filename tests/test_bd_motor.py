import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bd_catalogo import ErroCatalogo
from bd_motor import MotorSQL
from bd_planejador import ScanIndice, ScanSeq
from bd_sql_parser import ErroSQL
from bd_volcano import ErroExecucao


def motor():
    m = MotorSQL()
    m.executar("CREATE TABLE usuarios (id INT PRIMARY KEY, nome TEXT, idade INT, saldo REAL)")
    m.executar("CREATE TABLE pedidos (id INT PRIMARY KEY, uid INT, valor REAL)")
    m.executar("""INSERT INTO usuarios VALUES (1, 'ana', 30, 10), (2, 'bia', NULL, 20.5),
                  (3, 'caio', 17, 0), (4, 'ana', 45, 99)""")
    m.executar("INSERT INTO pedidos VALUES (10, 1, 5.0), (11, 1, 7.5), (12, 3, 1.0), (13, 9, 2.0)")
    return m


class TestMotor(unittest.TestCase):
    def setUp(self):
        self.m = motor()

    def q(self, sql):
        return self.m.executar(sql).linhas

    def test_select_basico_e_estrela(self):
        r = self.m.executar("SELECT * FROM usuarios WHERE id = 2")
        self.assertEqual(r.colunas, ["id", "nome", "idade", "saldo"])
        self.assertEqual(r.linhas, [(2, "bia", None, 20.5)])

    def test_inteiro_vira_real_na_insercao(self):
        self.assertEqual(self.q("SELECT saldo FROM usuarios WHERE id = 1"), [(10.0,)])
        self.assertIsInstance(self.q("SELECT saldo FROM usuarios WHERE id = 1")[0][0], float)

    def test_where_com_null_e_ordem(self):
        self.assertEqual(self.q("SELECT id FROM usuarios WHERE idade >= 18 ORDER BY id DESC"), [(4,), (1,)])
        self.assertEqual(self.q("SELECT id FROM usuarios WHERE idade IS NULL"), [(2,)])

    def test_alias_na_ordenacao_e_limite_distinto(self):
        self.assertEqual(self.q("SELECT nome n, id FROM usuarios ORDER BY n DESC, id LIMIT 2"),
                         [("caio", 3), ("bia", 2)])
        self.assertEqual(self.q("SELECT DISTINCT nome FROM usuarios ORDER BY nome"),
                         [("ana",), ("bia",), ("caio",)])
        self.assertEqual(self.q("SELECT idade * 2 AS dobro FROM usuarios ORDER BY dobro LIMIT 1"), [(None,)])

    def test_juncao_hash_e_loop(self):
        r = self.q("SELECT u.nome, p.valor FROM usuarios u JOIN pedidos p ON p.uid = u.id ORDER BY p.valor")
        self.assertEqual(r, [("caio", 1.0), ("ana", 5.0), ("ana", 7.5)])
        r = self.q("SELECT u.id, p.id FROM usuarios u JOIN pedidos p ON p.valor > u.saldo ORDER BY u.id, p.id")
        self.assertEqual(r, [(3, 10), (3, 11), (3, 12), (3, 13)])

    def test_juncao_tripla(self):
        self.m.executar("CREATE TABLE itens (id INT PRIMARY KEY, pid INT, nome TEXT)")
        self.m.executar("INSERT INTO itens VALUES (1, 10, 'x'), (2, 10, 'y'), (3, 12, 'z')")
        r = self.q("""SELECT u.nome, i.nome FROM usuarios u JOIN pedidos p ON p.uid = u.id
                      JOIN itens i ON i.pid = p.id ORDER BY i.nome""")
        self.assertEqual(r, [("ana", "x"), ("ana", "y"), ("caio", "z")])

    def test_group_by_having_order(self):
        r = self.q("""SELECT nome, COUNT(*) AS n, SUM(saldo) FROM usuarios GROUP BY nome
                      HAVING COUNT(*) >= 1 ORDER BY n DESC, nome""")
        self.assertEqual(r, [("ana", 2, 109.0), ("bia", 1, 20.5), ("caio", 1, 0.0)])
        self.assertEqual(self.q("SELECT COUNT(*), MAX(idade) FROM usuarios"), [(4, 45)])
        self.assertEqual(self.q("SELECT COUNT(*) FROM usuarios WHERE id > 100"), [(0,)])

    def test_group_com_juncao(self):
        r = self.q("""SELECT u.nome, SUM(p.valor) total FROM usuarios u JOIN pedidos p ON p.uid = u.id
                      GROUP BY u.nome ORDER BY total DESC""")
        self.assertEqual(r, [("ana", 12.5), ("caio", 1.0)])

    def test_indice_e_varredura_dao_o_mesmo_resultado(self):
        for i in range(100, 400):
            self.m.executar(f"INSERT INTO usuarios VALUES ({i}, 'u{i}', {i % 50}, {i})")
        self.m.executar("INSERT INTO usuarios VALUES (1000, 'x', 20, 0)")
        com = self.m.executar("SELECT id FROM usuarios WHERE id BETWEEN 120 AND 130 ORDER BY id")
        self.assertIsInstance(com.plano.raiz, ScanIndice)
        sem = self.m.executar("SELECT id FROM usuarios WHERE id + 0 BETWEEN 120 AND 130 ORDER BY id")
        self.assertIsInstance(sem.plano.raiz, ScanSeq)
        self.assertEqual(com.linhas, sem.linhas)
        self.assertEqual(len(com.linhas), 11)
        ab = self.m.executar("SELECT id FROM usuarios WHERE id > 395 AND id < 1000 ORDER BY id")
        self.assertEqual(ab.linhas, [(396,), (397,), (398,), (399,)])

    def test_indice_secundario(self):
        for i in range(100, 600):
            self.m.executar(f"INSERT INTO pedidos VALUES ({i}, {i % 100}, 1.5)")
        self.m.criar_indice("idx_uid", "pedidos", "uid")
        r = self.m.executar("SELECT COUNT(*) FROM pedidos WHERE uid = 7")
        self.assertIsInstance(r.plano.raiz, ScanIndice)
        self.assertEqual(r.linhas, [(5,)])

    def test_update_e_delete(self):
        self.assertEqual(self.m.executar("UPDATE usuarios SET saldo = saldo + 1, nome = 'z' WHERE idade > 20").afetadas, 2)
        self.assertEqual(self.q("SELECT nome, saldo FROM usuarios WHERE id IN (1, 4) ORDER BY id"),
                         [("z", 11.0), ("z", 100.0)])
        self.assertEqual(self.m.executar("DELETE FROM usuarios WHERE nome = 'z'").afetadas, 2)
        self.assertEqual(self.q("SELECT id FROM usuarios ORDER BY id"), [(2,), (3,)])
        self.assertEqual(self.q("SELECT id FROM usuarios WHERE id = 1"), [])  # índice atualizado
        self.assertEqual(self.m.executar("DELETE FROM usuarios").afetadas, 2)

    def test_update_le_valores_antigos(self):
        self.m.executar("CREATE TABLE p (a INT, b INT)")
        self.m.executar("INSERT INTO p VALUES (1, 2)")
        self.m.executar("UPDATE p SET a = b, b = a")
        self.assertEqual(self.q("SELECT a, b FROM p"), [(2, 1)])

    def test_atomicidade_em_falhas(self):
        antes = self.q("SELECT * FROM usuarios ORDER BY id")
        with self.assertRaises(ErroExecucao):
            self.m.executar("INSERT INTO usuarios VALUES (10, 'a', 1, 1), (1, 'dup', 1, 1)")
        with self.assertRaises(ErroExecucao):
            self.m.executar("UPDATE usuarios SET id = 1 WHERE id = 2")
        with self.assertRaises(ErroExecucao):
            self.m.executar("UPDATE usuarios SET idade = 1 / 0")
        self.assertEqual(self.q("SELECT * FROM usuarios ORDER BY id"), antes)
        self.assertEqual(self.m.catalogo.tabela("usuarios").n_linhas, 4)

    def test_erros_de_insercao(self):
        for sql in ("INSERT INTO usuarios VALUES (NULL, 'a', 1, 1)",
                    "INSERT INTO usuarios VALUES ('x', 'a', 1, 1)",
                    "INSERT INTO usuarios (id, id) VALUES (9, 9)",
                    "INSERT INTO usuarios VALUES (9, 'a', 1)"):
            with self.assertRaises((ErroExecucao, ErroSQL), msg=sql):
                self.m.executar(sql)
        with self.assertRaises(ErroCatalogo):
            self.m.executar("INSERT INTO usuarios (zzz) VALUES (1)")

    def test_insert_com_subconjunto_de_colunas(self):
        self.m.executar("INSERT INTO usuarios (id, nome) VALUES (50, 'z')")
        self.assertEqual(self.q("SELECT idade, saldo FROM usuarios WHERE id = 50"), [(None, None)])

    def test_indice_unico_e_duplicados_existentes(self):
        with self.assertRaises(ErroExecucao):
            self.m.criar_indice("u_nome", "usuarios", "nome", unico=True)  # 'ana' repetida
        self.m.criar_indice("u_idade", "usuarios", "idade", unico=True)  # NULL único é permitido
        self.m.executar("INSERT INTO usuarios (id, idade) VALUES (60, NULL)")
        with self.assertRaises(ErroExecucao):
            self.m.executar("INSERT INTO usuarios (id, idade) VALUES (61, 30)")

    def test_tabela_e_coluna_inexistentes(self):
        with self.assertRaises(ErroCatalogo):
            self.q("SELECT * FROM fantasma")
        with self.assertRaises(ErroExecucao):
            self.q("SELECT zzz FROM usuarios")
        with self.assertRaises(ErroExecucao):
            self.q("SELECT id FROM usuarios u JOIN pedidos p ON p.uid = u.id")  # id ambíguo
        with self.assertRaises(ErroCatalogo):
            self.m.executar("CREATE TABLE usuarios (a INT)")

    def test_tabela_vazia(self):
        self.m.executar("CREATE TABLE vazia (a INT)")
        self.assertEqual(self.q("SELECT * FROM vazia"), [])
        self.assertEqual(self.q("SELECT COUNT(*) FROM vazia"), [(0,)])
        self.assertEqual(self.q("SELECT * FROM vazia v JOIN usuarios u ON v.a = u.id"), [])


if __name__ == "__main__":
    unittest.main()
