import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dt_processo_cnj import montar_processo
from jur_processos import Fase, Parte, Polo, adicionar_parte, avancar_fase, criar_processo

NUM = montar_processo(1234, 2024, 8, 26, 100)


class TestProcessos(unittest.TestCase):
    def test_criar(self):
        p = criar_processo(NUM.replace("-", "").replace(".", ""), " Cível ", "Dra. Ana", "1500.50")
        self.assertEqual(p.numero, NUM)
        self.assertEqual(p.area, "cível")
        self.assertEqual(p.valor_causa, Decimal("1500.50"))
        self.assertEqual(p.tribunal, "26")

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            criar_processo("0000000-00.2024.8.26.0100", "civel", "A", 1)
        with self.assertRaises(ValueError):
            criar_processo(NUM, "civel", "A", -1)
        with self.assertRaises(ValueError):
            criar_processo(NUM, " ", "A", 1)

    def test_partes(self):
        p = criar_processo(NUM, "civel", "A", 10)
        p = adicionar_parte(p, Parte("João", Polo.ATIVO, 1))
        p = adicionar_parte(p, Parte("Banco X", Polo.PASSIVO))
        self.assertEqual(len(p.partes_do_polo(Polo.PASSIVO)), 1)
        self.assertEqual([x.nome for x in p.nosso_cliente()], ["João"])
        with self.assertRaises(ValueError):
            adicionar_parte(p, Parte("joão", Polo.ATIVO))
        with self.assertRaises(ValueError):
            adicionar_parte(p, Parte("JOÃO", Polo.PASSIVO))

    def test_fases(self):
        p = criar_processo(NUM, "civel", "A", 10)
        p2 = avancar_fase(p, Fase.EXECUCAO)
        self.assertEqual(p.fase, Fase.CONHECIMENTO)
        self.assertEqual(p2.fase, Fase.EXECUCAO)
        with self.assertRaises(ValueError):
            avancar_fase(p2, Fase.RECURSAL)
        with self.assertRaises(ValueError):
            avancar_fase(p2, Fase.EXECUCAO)


if __name__ == "__main__":
    unittest.main()
