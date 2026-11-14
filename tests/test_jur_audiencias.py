import sys
import unittest
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from jur_audiencias import Agenda, Audiencia


def D(h: int, m: int = 0) -> datetime:
    return datetime(2024, 5, 10, h, m)


class TestAgenda(unittest.TestCase):
    def setUp(self):
        self.ag = Agenda()
        self.ag.agendar(Audiencia("P1", D(10), 60, "Sala 1", "Ana"))

    def test_conflito_advogado(self):
        with self.assertRaisesRegex(ValueError, "advogado"):
            self.ag.agendar(Audiencia("P2", D(10, 30), 30, "Sala 2", "Ana"))

    def test_conflito_local(self):
        with self.assertRaisesRegex(ValueError, "local"):
            self.ag.agendar(Audiencia("P2", D(10, 59), 30, "Sala 1", "Bia"))

    def test_encostar_nao_conflita(self):
        self.ag.agendar(Audiencia("P2", D(11), 30, "Sala 1", "Ana"))
        self.assertEqual(len(self.ag), 2)

    def test_folga(self):
        ag = Agenda(folga_min=30)
        ag.agendar(Audiencia("P1", D(10), 60, "S1", "Ana"))
        with self.assertRaises(ValueError):
            ag.agendar(Audiencia("P2", D(11), 30, "S2", "Ana"))
        ag.agendar(Audiencia("P3", D(11, 30), 30, "S2", "Ana"))

    def test_duplicada(self):
        with self.assertRaisesRegex(ValueError, "duplicada"):
            self.ag.agendar(Audiencia("P1", D(10), 15, "Sala 9", "Zed"))

    def test_duracao_invalida(self):
        with self.assertRaises(ValueError):
            Audiencia("P", D(9), 0, "S", "A")

    def test_consultas(self):
        self.ag.agendar(Audiencia("P2", D(8), 30, "S2", "Bia"))
        self.assertEqual([a.processo for a in self.ag.do_dia(date(2024, 5, 10))], ["P2", "P1"])
        self.assertEqual(self.ag.do_dia(date(2024, 5, 11)), [])
        self.assertEqual(self.ag.proxima(D(9)).processo, "P1")
        self.assertIsNone(self.ag.proxima(D(12)))
        self.assertEqual(len(self.ag.do_advogado("Ana")), 1)

    def test_cancelar(self):
        self.assertTrue(self.ag.cancelar("P1", D(10)))
        self.assertFalse(self.ag.cancelar("P1", D(10)))

    def test_livres(self):
        livres = self.ag.horarios_livres(date(2024, 5, 10), "Ana", 60, abre=9, fecha=12)
        self.assertEqual(livres, [D(9), D(11)])


if __name__ == "__main__":
    unittest.main()
