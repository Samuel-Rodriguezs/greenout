import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from jur_ciclo import TRANSICOES, CicloProcesso, Estado, TransicaoInvalida


class TestCiclo(unittest.TestCase):
    def test_caminho_feliz(self):
        c = CicloProcesso()
        c.transitar(Estado.EM_ANDAMENTO, date(2024, 1, 1))
        c.transitar(Estado.SENTENCIADO, date(2024, 6, 1))
        c.transitar(Estado.TRANSITADO, date(2024, 8, 1))
        c.transitar(Estado.EM_EXECUCAO, date(2024, 9, 1))
        c.transitar(Estado.ARQUIVADO, date(2024, 12, 1))
        self.assertTrue(c.finalizado)
        self.assertEqual(len(c.historico), 5)

    def test_transicao_invalida(self):
        c = CicloProcesso()
        with self.assertRaises(TransicaoInvalida):
            c.transitar(Estado.SENTENCIADO, date(2024, 1, 1))
        self.assertEqual(c.estado, Estado.CADASTRADO)
        self.assertEqual(c.historico, [])

    def test_suspensao_exige_motivo(self):
        c = CicloProcesso(Estado.EM_ANDAMENTO)
        with self.assertRaises(ValueError):
            c.transitar(Estado.SUSPENSO, date(2024, 1, 1), "  ")
        c.transitar(Estado.SUSPENSO, date(2024, 1, 1), "acordo em negociação")
        self.assertEqual(c.historico[0].motivo, "acordo em negociação")

    def test_data_nao_regride(self):
        c = CicloProcesso()
        c.transitar(Estado.EM_ANDAMENTO, date(2024, 5, 1))
        with self.assertRaises(ValueError):
            c.transitar(Estado.ARQUIVADO, date(2024, 4, 1))

    def test_recurso_pode_voltar_a_sentenca(self):
        c = CicloProcesso(Estado.SENTENCIADO)
        c.transitar(Estado.EM_RECURSO, date(2024, 1, 1))
        self.assertTrue(c.pode(Estado.SENTENCIADO))

    def test_desarquivamento(self):
        c = CicloProcesso(Estado.ARQUIVADO)
        self.assertEqual(c.destinos(), [Estado.EM_ANDAMENTO])

    def test_tempo_em_estado(self):
        c = CicloProcesso()
        c.transitar(Estado.EM_ANDAMENTO, date(2024, 1, 1))
        c.transitar(Estado.SUSPENSO, date(2024, 1, 11), "x")
        c.transitar(Estado.EM_ANDAMENTO, date(2024, 1, 21))
        self.assertEqual(c.tempo_em(Estado.SUSPENSO, date(2024, 3, 1)), 10)
        self.assertEqual(c.tempo_em(Estado.EM_ANDAMENTO, date(2024, 1, 31)), 10 + 10)

    def test_alcancaveis_e_tabela_completa(self):
        self.assertEqual(set(TRANSICOES), set(Estado))
        self.assertIn(Estado.EM_EXECUCAO, CicloProcesso().alcancaveis())
        self.assertNotIn(Estado.CADASTRADO, CicloProcesso().alcancaveis())


if __name__ == "__main__":
    unittest.main()
