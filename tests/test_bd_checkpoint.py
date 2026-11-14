import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bd_checkpoint import BancoCheckpoint


class TestCheckpoint(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.caminho = os.path.join(self.dir.name, "wal.log")
        self.db = BancoCheckpoint(self.caminho)

    def tearDown(self):
        self.dir.cleanup()

    def _linhas(self):
        with open(self.caminho, encoding="utf-8") as f:
            return f.readlines()

    def test_checkpoint_trunca_log_sem_transacoes_ativas(self):
        for i in range(5):
            t = self.db.iniciar()
            self.db.escrever(t, f"k{i}", i)
            self.db.commit(t)
        antes = len(self.db.log.duravel)
        descartados = self.db.checkpoint()
        self.assertGreaterEqual(descartados, antes)
        self.assertEqual(len(self._linhas()), 1)  # só o registro CHECKPOINT
        self.assertEqual(self.db.disco.valores(), {f"k{i}": i for i in range(5)})

    def test_recuperacao_depois_do_checkpoint(self):
        t = self.db.iniciar()
        self.db.escrever(t, "a", 1)
        self.db.commit(t)
        self.db.checkpoint()
        u = self.db.iniciar()
        self.db.escrever(u, "b", 2)
        self.db.commit(u)
        novo = self.db.crash()
        novo.recuperar()
        self.assertEqual(novo.disco.valores(), {"a": 1, "b": 2})

    def test_transacao_ativa_atravessando_checkpoint_e_desfeita(self):
        base = self.db.iniciar()
        self.db.escrever(base, "x", "ok")
        self.db.commit(base)
        perdedora = self.db.iniciar()
        self.db.escrever(perdedora, "x", "ruim")
        self.db.checkpoint()  # grava "ruim" no disco, mas mantém o log da perdedora
        self.assertEqual(self.db.disco.valores()["x"], "ruim")
        self.db.escrever(perdedora, "y", "ruim2")
        self.db.log.forcar()
        novo = self.db.crash()
        r = novo.recuperar()
        self.assertEqual(r["perdedores"], [perdedora])
        self.assertEqual(novo.disco.valores(), {"x": "ok"})

    def test_transacao_ativa_pode_commitar_apos_checkpoint(self):
        t = self.db.iniciar()
        self.db.escrever(t, "a", 1)
        self.db.checkpoint()
        self.db.escrever(t, "b", 2)
        self.db.commit(t)
        novo = self.db.crash()
        novo.recuperar()
        self.assertEqual(novo.disco.valores(), {"a": 1, "b": 2})

    def test_checkpoint_sem_truncar(self):
        t = self.db.iniciar()
        self.db.escrever(t, "a", 1)
        self.db.commit(t)
        self.db.log.forcar()
        n = len(self.db.log.duravel)
        self.assertEqual(self.db.checkpoint(truncar=False), 0)
        self.assertEqual(len(self.db.log.duravel), n + 1)
        self.assertEqual(self.db.checkpoints, 1)

    def test_checkpoint_repetido_e_idempotente(self):
        t = self.db.iniciar()
        self.db.escrever(t, "a", 1)
        self.db.commit(t)
        self.db.checkpoint()
        self.db.checkpoint()
        novo = self.db.crash()
        novo.recuperar()
        self.assertEqual(novo.disco.valores(), {"a": 1})
        self.assertFalse(os.path.exists(self.caminho + ".tmp"))


if __name__ == "__main__":
    unittest.main()
