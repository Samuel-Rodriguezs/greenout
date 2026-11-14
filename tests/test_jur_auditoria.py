import sys
import unittest
from dataclasses import replace
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from jur_auditoria import GENESIS, LogAuditoria, verificar_cadeia


def T(m: int) -> datetime:
    return datetime(2024, 5, 10, 9, m)


def montar() -> LogAuditoria:
    log = LogAuditoria()
    log.registrar(T(0), "ana", "criar_processo", {"numero": "1"})
    log.registrar(T(5), "bia", "editar_prazo", {"de": "10/05", "para": "17/05"})
    log.registrar(T(9), "ana", "emitir_recibo")
    return log


class TestAuditoria(unittest.TestCase):
    def test_encadeamento(self):
        log = montar()
        r = log.registros
        self.assertEqual(r[0].hash_anterior, GENESIS)
        self.assertEqual(r[1].hash_anterior, r[0].hash)
        self.assertEqual(r[2].hash_anterior, r[1].hash)
        self.assertEqual(len({x.hash for x in r}), 3)
        self.assertIsNone(log.verificar())

    def test_deterministico(self):
        self.assertEqual([r.hash for r in montar().registros], [r.hash for r in montar().registros])

    def test_adulteracao_de_conteudo(self):
        regs = list(montar().registros)
        regs[1] = replace(regs[1], detalhes={"de": "10/05", "para": "30/05"})
        self.assertEqual(verificar_cadeia(regs), 1)

    def test_adulteracao_recalculando_hash_quebra_proximo(self):
        regs = list(montar().registros)
        regs[0] = replace(regs[0], usuario="mallory")
        self.assertEqual(verificar_cadeia(regs), 0)

    def test_remocao_de_registro(self):
        regs = list(montar().registros)
        del regs[1]
        self.assertEqual(verificar_cadeia(regs), 1)

    def test_detalhes_isolados(self):
        det = {"k": "v"}
        log = LogAuditoria()
        log.registrar(T(0), "ana", "x", det)
        det["k"] = "alterado"
        self.assertEqual(log.registros[0].detalhes, {"k": "v"})

    def test_validacoes(self):
        log = montar()
        with self.assertRaises(ValueError):
            log.registrar(T(1), "ana", "retroativo")
        with self.assertRaises(ValueError):
            log.registrar(T(30), " ", "x")
        self.assertEqual(len(log), 3)

    def test_consulta_e_vazio(self):
        self.assertEqual(len(montar().do_usuario("ana")), 2)
        self.assertIsNone(LogAuditoria().verificar())

    def test_registros_e_tupla(self):
        self.assertIsInstance(montar().registros, tuple)


if __name__ == "__main__":
    unittest.main()
