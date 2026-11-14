import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bd_wal import BancoWAL


class TestWAL(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.caminho = os.path.join(self.dir.name, "wal.log")
        self.db = BancoWAL(self.caminho)

    def tearDown(self):
        self.dir.cleanup()

    def test_commit_sobrevive_ao_crash_sem_flush_de_paginas(self):
        t = self.db.iniciar()
        self.db.escrever(t, "a", 1)
        self.db.escrever(t, "b", 2)
        self.db.commit(t)
        self.assertEqual(self.db.disco.valores(), {})  # nada no disco ainda
        novo = self.db.crash()
        novo.recuperar()
        self.assertEqual(novo.disco.valores(), {"a": 1, "b": 2})
        self.assertEqual(novo.ler("a"), 1)

    def test_nao_commitada_sem_steal_desaparece(self):
        t = self.db.iniciar()
        self.db.escrever(t, "a", 1)
        novo = self.db.crash()
        r = novo.recuperar()
        self.assertEqual(novo.disco.valores(), {})
        self.assertEqual(r["perdedores"], [])  # BEGIN/UPDATE nem chegaram ao log durável

    def test_steal_exige_undo(self):
        t0 = self.db.iniciar()
        self.db.escrever(t0, "x", "velho")
        self.db.commit(t0)
        self.db.descarregar_tudo()
        t = self.db.iniciar()
        self.db.escrever(t, "x", "sujo")
        self.db.descarregar("x")  # página suja vai ao disco antes do commit
        self.assertEqual(self.db.disco.valores()["x"], "sujo")
        novo = self.db.crash()
        r = novo.recuperar()
        self.assertEqual(r["perdedores"], [t])
        self.assertEqual(novo.disco.valores()["x"], "velho")

    def test_regra_wal_forca_log_antes_da_pagina(self):
        t = self.db.iniciar()
        self.db.escrever(t, "k", 5)
        self.assertEqual(self.db.log.lsn_forcado, 0)
        self.db.descarregar("k")
        self.assertGreaterEqual(self.db.log.lsn_forcado, 2)

    def test_recuperacao_idempotente(self):
        t = self.db.iniciar()
        self.db.escrever(t, "a", 1)
        self.db.commit(t)
        u = self.db.iniciar()
        self.db.escrever(u, "a", 99)
        self.db.escrever(u, "b", 7)
        self.db.descarregar_tudo()
        n1 = self.db.crash()
        n1.recuperar()
        estado = dict(n1.disco.valores())
        self.assertEqual(estado, {"a": 1})
        n2 = n1.crash()  # crash logo após/durante recuperação: repete
        r = n2.recuperar()
        self.assertEqual(n2.disco.valores(), estado)
        self.assertEqual(r["desfeitos"], [])

    def test_abortar_desfaz_e_registra_clr(self):
        t = self.db.iniciar()
        self.db.escrever(t, "a", 1)
        self.db.commit(t)
        u = self.db.iniciar()
        self.db.escrever(u, "a", 2)
        self.db.escrever(u, "z", 3)
        self.db.abortar(u)
        self.assertEqual(self.db.ler("a"), 1)
        self.assertIsNone(self.db.ler("z"))
        tipos = [r["tipo"] for r in self.db.log.todos()]
        self.assertEqual(tipos.count("CLR"), 2)
        with self.assertRaises(KeyError):
            self.db.commit(u)

    def test_crash_no_meio_do_aborto(self):
        t = self.db.iniciar()
        self.db.escrever(t, "a", "v0")
        self.db.commit(t)
        u = self.db.iniciar()
        self.db.escrever(u, "a", "v1")
        self.db.escrever(u, "a", "v2")
        self.db.abortar(u)
        self.db.log.forcar()
        # remove o END final para simular crash antes de terminar o aborto
        with open(self.caminho, "r", encoding="utf-8") as f:
            linhas = f.readlines()
        self.assertIn('"END"', linhas[-1])
        with open(self.caminho, "w", encoding="utf-8") as f:
            f.writelines(linhas[:-3])  # perde END e os dois últimos registros
        novo = self.db.crash()
        r = novo.recuperar()
        self.assertEqual(r["perdedores"], [u])
        self.assertEqual(novo.disco.valores()["a"], "v0")

    def test_cauda_rasgada_do_log_e_ignorada(self):
        t = self.db.iniciar()
        self.db.escrever(t, "a", 1)
        self.db.commit(t)
        with open(self.caminho, "a", encoding="utf-8") as f:
            f.write('{"lsn": 99, "tipo": "UPD')  # escrita parcial no crash
        novo = self.db.crash()
        novo.recuperar()
        self.assertEqual(novo.disco.valores(), {"a": 1})

    def test_valor_apagado_none(self):
        t = self.db.iniciar()
        self.db.escrever(t, "a", 1)
        self.db.commit(t)
        u = self.db.iniciar()
        self.db.escrever(u, "a", None)
        self.db.commit(u)
        novo = self.db.crash()
        novo.recuperar()
        self.assertEqual(novo.disco.valores(), {})

    def test_tx_inativa(self):
        with self.assertRaises(KeyError):
            self.db.escrever(42, "a", 1)

    def test_ids_de_tx_continuam_apos_reabrir(self):
        t = self.db.iniciar()
        self.db.commit(t)
        novo = self.db.crash()
        self.assertGreater(novo.iniciar(), t)


if __name__ == "__main__":
    unittest.main()
