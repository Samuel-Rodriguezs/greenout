import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from jur_andamentos import Andamento, LinhaDoTempo


def montar() -> LinhaDoTempo:
    t = LinhaDoTempo()
    t.registrar(Andamento("P1", date(2024, 3, 10), "Sentença publicada", "decisão"))
    t.registrar(Andamento("P1", date(2024, 1, 5), "Petição inicial protocolada", "petição"))
    t.registrar(Andamento("P1", date(2024, 2, 1), "Citação", "movimentação"))
    t.registrar(Andamento("P2", date(2023, 12, 1), "Distribuição"))
    return t


class TestAndamentos(unittest.TestCase):
    def test_ordem(self):
        t = montar()
        self.assertEqual([a.descricao for a in t.do_processo("P1")],
                         ["Petição inicial protocolada", "Citação", "Sentença publicada"])
        self.assertEqual(t.do_processo("P1", recentes_primeiro=True)[0].descricao, "Sentença publicada")

    def test_ultimo_e_vazio(self):
        t = montar()
        self.assertEqual(t.ultimo("P1").data, date(2024, 3, 10))
        self.assertIsNone(t.ultimo("P9"))
        self.assertIsNone(t.dias_sem_movimento("P9", date(2024, 1, 1)))

    def test_filtros(self):
        t = montar()
        self.assertEqual(len(t.entre("P1", date(2024, 1, 5), date(2024, 2, 1))), 2)
        self.assertEqual(len(t.por_tipo("P1", "decisão")), 1)

    def test_parados(self):
        t = montar()
        self.assertEqual(t.dias_sem_movimento("P1", date(2024, 3, 20)), 10)
        self.assertEqual(t.parados(date(2024, 3, 20), 30), ["P2"])
        self.assertEqual(t.parados(date(2024, 3, 20), 5), ["P1", "P2"])

    def test_validacoes(self):
        t = montar()
        with self.assertRaises(ValueError):
            t.registrar(Andamento("P1", date(2024, 1, 1), "  "))
        with self.assertRaises(ValueError):
            t.registrar(Andamento("P2", date(2023, 12, 1), "Distribuição"))

    def test_texto(self):
        self.assertEqual(montar().texto("P2"), "01/12/2023 - [movimentação] Distribuição")


if __name__ == "__main__":
    unittest.main()
