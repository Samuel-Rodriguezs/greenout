import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from rede_rip import INFINITO, RedeRIP, Roteador


def linha(split=True):
    r = RedeRIP(split)
    r.adicionar_enlace("A", "B")
    r.adicionar_enlace("B", "C")
    r.adicionar_enlace("C", "D")
    return r


class TestRedeRip(unittest.TestCase):
    def test_convergencia_linha(self):
        r = linha()
        r.convergir()
        a = r.roteadores["A"]
        self.assertEqual([a.custo(x) for x in "ABCD"], [0, 1, 2, 3])
        self.assertEqual(a.tabela["D"], (3, "B"))
        self.assertEqual(r.roteadores["D"].tabela["A"], (3, "C"))

    def test_menor_caminho_com_custos(self):
        r = RedeRIP()
        r.adicionar_enlace("A", "B", 1)
        r.adicionar_enlace("B", "C", 1)
        r.adicionar_enlace("A", "C", 5)
        r.convergir()
        self.assertEqual(r.roteadores["A"].tabela["C"], (2, "B"))

    def test_split_horizon_poison_reverse(self):
        r = linha()
        r.convergir()
        b = r.roteadores["B"]
        self.assertEqual(b.anunciar("A")["D"], 2)  # D foi aprendido via C: pode contar a A
        self.assertEqual(b.anunciar("C")["D"], INFINITO)  # mas envenena de volta para C
        self.assertEqual(b.anunciar("A")["A"], INFINITO)
        self.assertEqual(b.anunciar("C")["A"], 1)
        self.assertEqual(b.anunciar("A")["B"], 0)

    def test_queda_de_enlace_sem_loop(self):
        r = linha(True)
        r.convergir()
        r.derrubar_enlace("C", "D")
        r.convergir()
        self.assertEqual(r.roteadores["A"].custo("D"), INFINITO)
        self.assertEqual(r.roteadores["C"].custo("D"), INFINITO)

    def test_contagem_ao_infinito_sem_split_horizon(self):
        r = linha(False)
        r.convergir()
        r.derrubar_enlace("C", "D")
        rodadas = r.convergir()
        self.assertGreater(rodadas, 5)  # lento: contagem até 16
        self.assertEqual(r.roteadores["A"].custo("D"), INFINITO)

    def test_rota_alternativa_apos_queda(self):
        r = RedeRIP()
        for a, b in (("A", "B"), ("B", "C"), ("A", "D"), ("D", "C")):
            r.adicionar_enlace(a, b)
        r.convergir()
        self.assertEqual(r.roteadores["A"].custo("C"), 2)
        r.derrubar_enlace("B", "C")
        r.convergir()
        self.assertEqual(r.roteadores["A"].tabela["C"], (2, "D"))
        self.assertEqual(r.roteadores["B"].tabela["C"], (3, "A"))

    def test_nao_ultrapassa_infinito(self):
        r = Roteador("X")
        r.vizinhos["Y"] = 1
        r.receber("Y", {"Z": 15})
        self.assertEqual(r.custo("Z"), INFINITO)

    def test_vizinho_desconhecido(self):
        with self.assertRaises(ValueError):
            Roteador("X").receber("Y", {})


if __name__ == "__main__":
    unittest.main()
