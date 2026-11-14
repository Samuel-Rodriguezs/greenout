import sys
import unittest
from datetime import date
from decimal import Decimal as D
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from jur_recibos import EmissorRecibos, Lancamento, conciliar


class TestRecibos(unittest.TestCase):
    def test_emissao_sequencial(self):
        e = EmissorRecibos()
        r1 = e.emitir(1, D("100"), date(2024, 1, 5), "parcela 1")
        r2 = e.emitir(1, D("100"), date(2024, 2, 5), "parcela 2")
        self.assertEqual((r1.numero, r2.numero), (1, 2))

    def test_invalidos(self):
        e = EmissorRecibos()
        with self.assertRaises(ValueError):
            e.emitir(1, D("0"), date(2024, 1, 1), "x")
        with self.assertRaises(ValueError):
            e.emitir(1, D("1"), date(2024, 1, 1), "  ")

    def test_texto(self):
        r = EmissorRecibos(7).emitir(1, D("1234.5"), date(2024, 3, 9), "honorários")
        t = r.texto("Maria")
        self.assertIn("Nº 000007", t)
        self.assertIn("R$ 1.234,50", t)
        self.assertIn("09/03/2024", t)

    def test_conciliacao(self):
        e = EmissorRecibos()
        r1 = e.emitir(1, D("100"), date(2024, 1, 5), "a")
        r2 = e.emitir(2, D("100"), date(2024, 1, 6), "b")
        r3 = e.emitir(3, D("50"), date(2024, 1, 7), "c")
        ext = [Lancamento(date(2024, 1, 5), D("100")), Lancamento(date(2024, 1, 7), D("100")),
               Lancamento(date(2024, 1, 20), D("50")), Lancamento(date(2024, 1, 8), D("-30"), "tarifa"),
               Lancamento(date(2024, 1, 9), D("77"))]
        c = conciliar(e.emitidos, ext)
        self.assertEqual([(r.numero, l.data.day) for r, l in c.pares], [(1, 5), (2, 7)])
        self.assertEqual(c.recibos_sem_lancamento, [r3])
        self.assertEqual(len(c.lancamentos_sem_recibo), 2)  # 50 fora da tolerância e 77
        self.assertFalse(c.conciliado)

    def test_conciliado_total(self):
        e = EmissorRecibos()
        e.emitir(1, D("10"), date(2024, 1, 1), "a")
        c = conciliar(e.emitidos, [Lancamento(date(2024, 1, 3), D("10"))])
        self.assertTrue(c.conciliado)

    def test_lancamento_usado_uma_vez(self):
        e = EmissorRecibos()
        e.emitir(1, D("10"), date(2024, 1, 1), "a")
        e.emitir(2, D("10"), date(2024, 1, 1), "b")
        c = conciliar(e.emitidos, [Lancamento(date(2024, 1, 1), D("10"))])
        self.assertEqual(len(c.pares), 1)
        self.assertEqual(len(c.recibos_sem_lancamento), 1)


if __name__ == "__main__":
    unittest.main()
