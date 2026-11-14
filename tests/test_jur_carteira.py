import sys
import unittest
from dataclasses import replace
from decimal import Decimal as D
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dt_processo_cnj import montar_processo
from jur_carteira import concentracao, por_advogado, resumo_por_area, total_carteira
from jur_processos import Fase, criar_processo


def proc(seq: int, area: str, adv: str, valor: str):
    return criar_processo(montar_processo(seq, 2024, 8, 26, 1), area, adv, valor)


CART = [proc(1, "civel", "Ana", "10000"), proc(2, "civel", "Bia", "30000"),
        proc(3, "trabalhista", "Ana", "60000"), proc(4, "familia", "Ana", "100")]


class TestCarteira(unittest.TestCase):
    def test_resumo(self):
        r = resumo_por_area(CART)
        self.assertEqual([l.area for l in r], ["trabalhista", "civel", "familia"])
        civel = r[1]
        self.assertEqual((civel.quantidade, civel.total, civel.media, civel.maior), (2, D("40000"), D("20000.00"), D("30000")))
        self.assertEqual(r[0].participacao, D("59.94"))
        self.assertEqual(total_carteira(CART), D("100100"))

    def test_encerrados(self):
        enc = replace(CART[3], fase=Fase.ENCERRADO)
        c = CART[:3] + [enc]
        self.assertEqual(len(resumo_por_area(c)), 2)
        self.assertEqual(len(resumo_por_area(c, incluir_encerrados=True)), 3)

    def test_vazia(self):
        self.assertEqual(resumo_por_area([]), [])
        self.assertEqual(total_carteira([]), D("0"))
        self.assertEqual(concentracao([]), D("0.00"))

    def test_zero_total(self):
        r = resumo_por_area([proc(5, "civel", "Ana", "0")])
        self.assertEqual(r[0].participacao, D("0.00"))

    def test_por_advogado(self):
        self.assertEqual(por_advogado(CART), {"Ana": (3, D("70100")), "Bia": (1, D("30000"))})

    def test_concentracao(self):
        self.assertEqual(concentracao(CART, 1), D("59.94"))
        self.assertEqual(concentracao(CART, 10), D("100.00"))


if __name__ == "__main__":
    unittest.main()
