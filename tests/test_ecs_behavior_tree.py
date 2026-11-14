import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_behavior_tree import (Acao, Condicao, Espera, Inversor, Paralelo, Repetir, SempreSucesso,
                               Seletor, Sequencia, Status)

S, F, E = Status.SUCESSO, Status.FALHA, Status.EXECUTANDO


def registra(log, nome, status):
    def fn(ctx):
        log.append(nome)
        return status
    return Acao(fn)


class TestBT(unittest.TestCase):
    def test_sequencia_para_na_falha(self):
        log = []
        t = Sequencia(registra(log, "a", S), registra(log, "b", F), registra(log, "c", S))
        self.assertIs(t.tick(None), F)
        self.assertEqual(log, ["a", "b"])

    def test_sequencia_retoma_filho_executando(self):
        log, estado = [], {"n": 0}

        def longa(ctx):
            estado["n"] += 1
            log.append("longa")
            return E if estado["n"] < 3 else S
        t = Sequencia(registra(log, "a", S), Acao(longa), registra(log, "c", S))
        self.assertIs(t.tick(None), E)
        self.assertIs(t.tick(None), E)
        self.assertIs(t.tick(None), S)
        self.assertEqual(log, ["a", "longa", "longa", "longa", "c"])  # "a" não repete

    def test_seletor(self):
        log = []
        t = Seletor(registra(log, "a", F), registra(log, "b", S), registra(log, "c", S))
        self.assertIs(t.tick(None), S)
        self.assertEqual(log, ["a", "b"])
        self.assertIs(Seletor(Condicao(lambda c: False)).tick(None), F)

    def test_condicao_usa_contexto(self):
        c = Condicao(lambda ctx: ctx["vida"] > 0)
        self.assertIs(c.tick({"vida": 1}), S)
        self.assertIs(c.tick({"vida": 0}), F)

    def test_inversor_e_sempre_sucesso(self):
        self.assertIs(Inversor(Acao(lambda c: S)).tick(None), F)
        self.assertIs(Inversor(Acao(lambda c: F)).tick(None), S)
        self.assertIs(Inversor(Acao(lambda c: E)).tick(None), E)
        self.assertIs(SempreSucesso(Acao(lambda c: F)).tick(None), S)
        self.assertIs(SempreSucesso(Acao(lambda c: E)).tick(None), E)

    def test_repetir(self):
        ctx = {"n": 0}

        def inc(c):
            c["n"] += 1
            return S
        t = Repetir(Acao(inc), 3)
        self.assertIs(t.tick(ctx), S)
        self.assertEqual(ctx["n"], 3)
        self.assertIs(Repetir(Acao(lambda c: F), 3).tick(None), F)

    def test_paralelo(self):
        self.assertIs(Paralelo(Acao(lambda c: S), Acao(lambda c: S)).tick(None), S)
        self.assertIs(Paralelo(Acao(lambda c: S), Acao(lambda c: F)).tick(None), F)
        self.assertIs(Paralelo(Acao(lambda c: S), Acao(lambda c: E)).tick(None), E)
        t = Paralelo(Acao(lambda c: S), Acao(lambda c: F), minimo_sucessos=1)
        self.assertIs(t.tick(None), S)

    def test_espera(self):
        e = Espera(2)
        self.assertEqual([e.tick(None) for _ in range(4)], [E, E, S, E])

    def test_ia_exemplo_completo(self):
        ctx = {"inimigo_perto": False, "ataques": 0}

        def atacar(c):
            c["ataques"] += 1
            return S
        arvore = Seletor(
            Sequencia(Condicao(lambda c: c["inimigo_perto"]), Acao(atacar)),
            Acao(lambda c: S),  # patrulha
        )
        arvore.tick(ctx)
        self.assertEqual(ctx["ataques"], 0)
        ctx["inimigo_perto"] = True
        arvore.tick(ctx)
        self.assertEqual(ctx["ataques"], 1)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            Sequencia()
        with self.assertRaises(ValueError):
            Repetir(Acao(lambda c: S), 0)
        with self.assertRaises(ValueError):
            Paralelo(Acao(lambda c: S), minimo_sucessos=2)


if __name__ == "__main__":
    unittest.main()
