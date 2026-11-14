import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from pa_enum_prioridade import Estado, Prioridade


class TestEnumPrioridade(unittest.TestCase):
    def test_ordenacao(self):
        ordenado = sorted([Prioridade.ALTA, Prioridade.BAIXA, Prioridade.MEDIA])
        self.assertEqual(ordenado[0], Prioridade.BAIXA)
        self.assertGreater(Prioridade.ALTA, Prioridade.MEDIA)

    def test_de_texto(self):
        self.assertIs(Prioridade.de_texto("  alta "), Prioridade.ALTA)
        with self.assertRaises(ValueError):
            Prioridade.de_texto("urgente")

    def test_escalar_com_teto(self):
        self.assertIs(Prioridade.BAIXA.escalar(), Prioridade.MEDIA)
        self.assertIs(Prioridade.ALTA.escalar(), Prioridade.ALTA)

    def test_transicoes_validas(self):
        e = Estado.ABERTO.transicionar(Estado.EM_ANDAMENTO).transicionar(Estado.CONCLUIDO)
        self.assertIs(e, Estado.CONCLUIDO)
        self.assertTrue(e.final)

    def test_transicoes_invalidas(self):
        with self.assertRaises(ValueError):
            Estado.ABERTO.transicionar(Estado.CONCLUIDO)
        with self.assertRaises(ValueError):
            Estado.CANCELADO.transicionar(Estado.ABERTO)

    def test_estado_nao_final(self):
        self.assertFalse(Estado.ABERTO.final)


if __name__ == "__main__":
    unittest.main()
