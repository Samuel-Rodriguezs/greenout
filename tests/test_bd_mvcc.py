import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bd_mvcc import BancoMVCC, ErroConflito, ErroTransacao


class TestMVCC(unittest.TestCase):
    def setUp(self):
        self.db = BancoMVCC()
        t = self.db.iniciar()
        t.escrever("x", 10)
        t.escrever("y", 20)
        t.commit()

    def test_leitura_do_proprio_escrito(self):
        t = self.db.iniciar()
        t.escrever("x", 11)
        self.assertEqual(t.ler("x"), 11)
        t.apagar("y")
        self.assertIsNone(t.ler("y"))
        self.assertEqual(t.chaves(), ["x"])

    def test_snapshot_ignora_commits_posteriores(self):
        leitor = self.db.iniciar()
        escritor = self.db.iniciar()
        escritor.escrever("x", 99)
        escritor.commit()
        self.assertEqual(leitor.ler("x"), 10)  # leitura repetível
        self.assertEqual(self.db.iniciar().ler("x"), 99)

    def test_sem_leitura_suja(self):
        escritor = self.db.iniciar()
        escritor.escrever("x", 555)
        leitor = self.db.iniciar()
        self.assertEqual(leitor.ler("x"), 10)

    def test_abort_descarta_escritas(self):
        t = self.db.iniciar()
        t.escrever("x", 1)
        t.abortar()
        self.assertEqual(self.db.iniciar().ler("x"), 10)
        with self.assertRaises(ErroTransacao):
            t.ler("x")

    def test_first_committer_wins(self):
        a, b = self.db.iniciar(), self.db.iniciar()
        a.escrever("x", 1)
        b.escrever("x", 2)
        a.commit()
        with self.assertRaises(ErroConflito):
            b.commit()
        self.assertEqual(self.db.iniciar().ler("x"), 1)
        self.assertFalse(b.ativa)

    def test_escritas_em_chaves_distintas_nao_conflitam(self):
        a, b = self.db.iniciar(), self.db.iniciar()
        a.escrever("x", 1)
        b.escrever("y", 2)
        a.commit()
        b.commit()
        t = self.db.iniciar()
        self.assertEqual((t.ler("x"), t.ler("y")), (1, 2))

    def test_write_skew_e_permitido_por_snapshot_isolation(self):
        # invariante desejada: x + y >= 0; cada tx vê x=10, y=20 e saca 25 de uma conta
        db = BancoMVCC()
        s = db.iniciar()
        s.escrever("x", 10)
        s.escrever("y", 10)
        s.commit()
        a, b = db.iniciar(), db.iniciar()
        if a.ler("x") + a.ler("y") >= 20:
            a.escrever("x", a.ler("x") - 20)
        if b.ler("x") + b.ler("y") >= 20:
            b.escrever("y", b.ler("y") - 20)
        a.commit()
        b.commit()  # conjuntos de escrita disjuntos: ambos passam
        f = db.iniciar()
        self.assertEqual(f.ler("x") + f.ler("y"), -20)

    def test_somente_leitura_sempre_comita(self):
        r = self.db.iniciar()
        r.ler("x")
        w = self.db.iniciar()
        w.escrever("x", 5)
        w.commit()
        self.assertEqual(r.commit(), r.snapshot)

    def test_apagar_e_ler_padrao(self):
        t = self.db.iniciar()
        t.apagar("x")
        t.commit()
        u = self.db.iniciar()
        self.assertEqual(u.ler("x", "nada"), "nada")
        self.assertEqual(u.chaves(), ["y"])

    def test_coleta_de_lixo_respeita_transacoes_ativas(self):
        velho = self.db.iniciar()
        for v in (1, 2, 3):
            t = self.db.iniciar()
            t.escrever("x", v)
            t.commit()
        antes = self.db.total_versoes()
        self.db.coletar_lixo()
        self.assertEqual(velho.ler("x"), 10)  # versão do snapshot antigo preservada
        velho.abortar()
        removidas = self.db.coletar_lixo()
        self.assertGreater(removidas, 0)
        self.assertLess(self.db.total_versoes(), antes)
        self.assertEqual(self.db.iniciar().ler("x"), 3)

    def test_gc_remove_chave_apagada(self):
        t = self.db.iniciar()
        t.apagar("y")
        t.commit()
        self.db.coletar_lixo()
        self.assertNotIn("y", self.db.versoes)

    def test_commit_duplo(self):
        t = self.db.iniciar()
        t.commit()
        with self.assertRaises(ErroTransacao):
            t.commit()


if __name__ == "__main__":
    unittest.main()
