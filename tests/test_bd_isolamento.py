import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bd_isolamento import (READ_COMMITTED, READ_UNCOMMITTED, REPEATABLE_READ,
                           SERIALIZABLE, BancoIsolamento, ErroSerializacao)


class TestAnomalias(unittest.TestCase):
    def test_nivel_invalido(self):
        with self.assertRaises(ValueError):
            BancoIsolamento().iniciar("XYZ")

    def test_leitura_suja_so_em_read_uncommitted(self):
        for nivel, esperado in ((READ_UNCOMMITTED, 999), (READ_COMMITTED, 100),
                                (REPEATABLE_READ, 100), (SERIALIZABLE, 100)):
            db = BancoIsolamento({"saldo": 100})
            escritor = db.iniciar()
            leitor = db.iniciar(nivel)
            escritor.escrever("saldo", 999)
            self.assertEqual(leitor.ler("saldo"), esperado, nivel)
            escritor.abortar()  # o valor lido em RU nunca existiu de fato
            self.assertEqual(db.comitado["saldo"], 100)

    def test_leitura_nao_repetivel(self):
        for nivel, repete in ((READ_COMMITTED, False), (REPEATABLE_READ, True), (SERIALIZABLE, True)):
            db = BancoIsolamento({"x": 1})
            t = db.iniciar(nivel)
            primeira = t.ler("x")
            w = db.iniciar()
            w.escrever("x", 2)
            w.commit()
            segunda = t.ler("x")
            self.assertEqual(primeira == segunda, repete, nivel)

    def test_fantasma_em_read_committed(self):
        db = BancoIsolamento({"a": 5, "b": 50})
        t = db.iniciar(READ_COMMITTED)
        self.assertEqual(set(t.varrer(lambda k, v: v > 10)), {"b"})
        w = db.iniciar()
        w.escrever("c", 70)
        w.commit()
        self.assertEqual(set(t.varrer(lambda k, v: v > 10)), {"b", "c"})

    def test_sem_fantasma_com_snapshot(self):
        db = BancoIsolamento({"b": 50})
        t = db.iniciar(REPEATABLE_READ)
        t.varrer(lambda k, v: v > 10)
        w = db.iniciar()
        w.escrever("c", 70)
        w.commit()
        self.assertEqual(set(t.varrer(lambda k, v: v > 10)), {"b"})

    def test_atualizacao_perdida_em_read_committed(self):
        db = BancoIsolamento({"n": 0})
        a, b = db.iniciar(READ_COMMITTED), db.iniciar(READ_COMMITTED)
        va, vb = a.ler("n"), b.ler("n")
        a.escrever("n", va + 1)
        b.escrever("n", vb + 1)
        a.commit()
        b.commit()
        self.assertEqual(db.comitado["n"], 1)  # deveria ser 2

    def test_atualizacao_perdida_evitada_em_repeatable_read(self):
        db = BancoIsolamento({"n": 0})
        a, b = db.iniciar(REPEATABLE_READ), db.iniciar(REPEATABLE_READ)
        a.escrever("n", a.ler("n") + 1)
        b.escrever("n", b.ler("n") + 1)
        a.commit()
        with self.assertRaises(ErroSerializacao):
            b.commit()
        self.assertEqual(db.comitado["n"], 1)

    def _write_skew(self, nivel):
        db = BancoIsolamento({"a": 1, "b": 1})  # regra: ao menos um plantonista (soma >= 1)
        t1, t2 = db.iniciar(nivel), db.iniciar(nivel)
        if t1.ler("a") + t1.ler("b") >= 2:
            t1.escrever("a", 0)
        if t2.ler("a") + t2.ler("b") >= 2:
            t2.escrever("b", 0)
        t1.commit()
        t2.commit()
        return db.comitado

    def test_write_skew_em_repeatable_read(self):
        estado = self._write_skew(REPEATABLE_READ)
        self.assertEqual(estado["a"] + estado["b"], 0)  # invariante violada

    def test_write_skew_barrado_em_serializable(self):
        with self.assertRaises(ErroSerializacao):
            self._write_skew(SERIALIZABLE)

    def test_fantasma_barrado_em_serializable(self):
        db = BancoIsolamento({"b": 50})
        t = db.iniciar(SERIALIZABLE)
        t.varrer(lambda k, v: v > 10)
        w = db.iniciar()
        w.escrever("c", 70)
        w.commit()
        t.escrever("resumo", 1)
        with self.assertRaises(ErroSerializacao):
            t.commit()
        self.assertNotIn("resumo", db.comitado)

    def test_serializable_sem_conflito_comita(self):
        db = BancoIsolamento({"x": 1})
        t = db.iniciar(SERIALIZABLE)
        t.ler("x")
        t.escrever("y", 2)
        t.commit()
        self.assertEqual(db.comitado, {"x": 1, "y": 2})

    def test_apagar_e_ler_proprias_escritas(self):
        db = BancoIsolamento({"x": 1})
        t = db.iniciar()
        t.apagar("x")
        self.assertIsNone(t.ler("x"))
        self.assertEqual(t.varrer(lambda k, v: True), {})
        t.commit()
        self.assertNotIn("x", db.comitado)

    def test_commit_apos_encerrar(self):
        t = BancoIsolamento().iniciar()
        t.commit()
        with self.assertRaises(RuntimeError):
            t.commit()


if __name__ == "__main__":
    unittest.main()
