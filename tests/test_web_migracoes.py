import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from web_migracoes import ErroMigracao, Migracao, Migrador

M1 = Migracao(1, "usuarios", "CREATE TABLE u (id INTEGER PRIMARY KEY, nome TEXT);",
              "DROP TABLE u;")
M2 = Migracao(2, "email", "ALTER TABLE u ADD COLUMN email TEXT;\nINSERT INTO u (nome) VALUES ('a;b');")
M3 = Migracao(3, "indice", "CREATE INDEX i ON u(nome);", "DROP INDEX i;")


def tabelas(con):
    return {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}


class TestWebMigracoes(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.addCleanup(self.con.close)

    def test_migrar_tudo_e_idempotente(self):
        m = Migrador(self.con, [M3, M1, M2])
        self.assertEqual(m.migrar(), [1, 2, 3])
        self.assertEqual(m.versao_atual(), 3)
        self.assertEqual(m.migrar(), [])
        self.assertEqual(self.con.execute("SELECT nome FROM u").fetchone()[0], "a;b")

    def test_alvo(self):
        m = Migrador(self.con, [M1, M2, M3])
        self.assertEqual(m.migrar(alvo=2), [1, 2])
        self.assertEqual([x.versao for x in m.pendentes()], [3])

    def test_reverter(self):
        m = Migrador(self.con, [M1, M3])
        m.migrar()
        self.assertEqual(m.reverter(), [3])
        self.assertEqual(m.reverter(5), [1])
        self.assertNotIn("u", tabelas(self.con))
        self.assertEqual(m.versao_atual(), 0)

    def test_irreversivel(self):
        m = Migrador(self.con, [M1, M2])
        m.migrar()
        with self.assertRaises(ErroMigracao):
            m.reverter()
        self.assertEqual(m.versao_atual(), 2)

    def test_falha_faz_rollback(self):
        ruim = Migracao(2, "ruim", "CREATE TABLE ok (a);\nINSERT INTO nao_existe VALUES (1);")
        m = Migrador(self.con, [M1, ruim])
        with self.assertRaises(ErroMigracao):
            m.migrar()
        self.assertEqual(m.versao_atual(), 1)
        self.assertNotIn("ok", tabelas(self.con))

    def test_checksum_alterado(self):
        Migrador(self.con, [M1]).migrar()
        alterada = Migracao(1, "usuarios", "CREATE TABLE u (id INTEGER);")
        with self.assertRaises(ErroMigracao):
            Migrador(self.con, [alterada]).migrar()

    def test_migracao_removida(self):
        Migrador(self.con, [M1, M3]).migrar()
        with self.assertRaises(ErroMigracao):
            Migrador(self.con, [M1]).migrar()

    def test_versoes_invalidas(self):
        with self.assertRaises(ErroMigracao):
            Migrador(self.con, [M1, M1])
        with self.assertRaises(ErroMigracao):
            Migrador(self.con, [Migracao(0, "x", "SELECT 1;")])


if __name__ == "__main__":
    unittest.main()
